//go:build !windows
// +build !windows

// Copyright 2022 Antrea Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package portcache

import (
	"fmt"

	"antrea.io/antrea/pkg/agent/nodeportlocal/rules"
)

// Some actions may be required on other platforms before adding NPL rules.
// Nothing to do on Linux.
func PrepareAddRule(protocolSocketData *ProtocolSocketData) error {
	return nil
}

// Close socket on linux.
func HandleCloseSocket(protocolSocketData *ProtocolSocketData) error {
	if err := protocolSocketData.socket.Close(); err != nil {
		return err
	}
	return nil
}

func (pt *PortTable) AddRule(podIP string, podPort int, protocol string) (int, error) {
	pt.tableLock.Lock()
	defer pt.tableLock.Unlock()
	npData := pt.getEntryByPodIPPort(podIP, podPort)
	exists := (npData != nil)
	if !exists {
		nodePort, protocols, err := pt.getFreePort(podIP, podPort)
		if err != nil {
			return 0, err
		}
		npData = &NodePortData{
			NodePort:  nodePort,
			PodIP:     podIP,
			PodPort:   podPort,
			Protocols: protocols,
		}
	}
	protocolSocketData := npData.FindProtocol(protocol)
	if protocolSocketData == nil {
		return 0, fmt.Errorf("unknown protocol %s", protocol)
	}
	if protocolSocketData.State == stateInUse {
		return 0, fmt.Errorf("rule for %s:%d:%s already exists", podIP, podPort, protocol)
	}
	if protocolSocketData.State == stateClosed {
		return 0, fmt.Errorf("invalid socket state for %s:%d:%s", podIP, podPort, protocol)
	}

	if err := PrepareAddRule(protocolSocketData); err != nil {
		return 0, err
	}

	nodePort := npData.NodePort
	if err := pt.PodPortRules.AddRule(nodePort, podIP, podPort, protocol); err != nil {
		return 0, err
	}

	protocolSocketData.State = stateInUse
	if !exists {
		pt.NodePortTable[nodePort] = npData
		pt.PodEndpointTable[podIPPortFormat(podIP, podPort)] = npData
	}
	return npData.NodePort, nil
}

// syncRules ensures that contents of the port table matches the iptables rules present on the Node.
func (pt *PortTable) syncRules() error {
	pt.tableLock.Lock()
	defer pt.tableLock.Unlock()
	nplPorts := make([]rules.PodNodePort, 0, len(pt.NodePortTable))
	for _, npData := range pt.NodePortTable {
		protocols := make([]string, 0, len(supportedProtocols))
		for i, protocol := range npData.Protocols {
			if protocol.State == stateInUse {
				protocols = append(protocols, protocol.Protocol)
				if err := PrepareAddRule(&npData.Protocols[i]); err != nil {
					return err
				}
			}
		}
		nplPorts = append(nplPorts, rules.PodNodePort{
			NodePort:  npData.NodePort,
			PodPort:   npData.PodPort,
			PodIP:     npData.PodIP,
			Protocols: protocols,
		})
	}
	if err := pt.PodPortRules.AddAllRules(nplPorts); err != nil {
		return err
	}
	return nil
}

func (pt *PortTable) DeleteRule(podIP string, podPort int, protocol string) error {
	pt.tableLock.Lock()
	defer pt.tableLock.Unlock()
	data := pt.getEntryByPodIPPort(podIP, podPort)
	if data == nil {
		// Delete not required when the PortTable entry does not exist
		return nil
	}
	numProtocolsInUse := 0
	var protocolSocketData *ProtocolSocketData
	for idx, pData := range data.Protocols {
		if pData.State != stateInUse {
			continue
		}
		numProtocolsInUse++
		if pData.Protocol == protocol {
			protocolSocketData = &data.Protocols[idx]
		}
	}
	if protocolSocketData != nil {
		if err := pt.PodPortRules.DeleteRule(data.NodePort, podIP, podPort, protocol); err != nil {
			return err
		}
		protocolSocketData.State = stateOpen
		numProtocolsInUse--
	}
	if numProtocolsInUse == 0 {
		// Node port is not needed anymore: close all sockets and delete
		// table entries.
		if err := data.CloseSockets(); err != nil {
			return err
		}
		delete(pt.NodePortTable, data.NodePort)
		delete(pt.PodEndpointTable, podIPPortFormat(podIP, podPort))
	}
	return nil
}

func (pt *PortTable) DeleteRulesForPod(podIP string) error {
	pt.tableLock.Lock()
	defer pt.tableLock.Unlock()
	podEntries := pt.getDataForPodIP(podIP)
	for _, podEntry := range podEntries {
		for len(podEntry.Protocols) > 0 {
			protocolSocketData := podEntry.Protocols[0]
			if err := pt.PodPortRules.DeleteRule(podEntry.NodePort, podIP, podEntry.PodPort, protocolSocketData.Protocol); err != nil {
				return err
			}
			if err := HandleCloseSocket(&protocolSocketData); err != nil {
				return fmt.Errorf("error when releasing local port %d with protocol %s: %v", podEntry.NodePort, protocolSocketData.Protocol, err)
			}
			podEntry.Protocols = podEntry.Protocols[1:]
		}
		delete(pt.NodePortTable, podEntry.NodePort)
		delete(pt.PodEndpointTable, podIPPortFormat(podIP, podEntry.PodPort))
	}
	return nil
}