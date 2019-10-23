// Copyright 2019 Antrea Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Code generated by client-gen. DO NOT EDIT.

package v1beta1

import (
	"time"

	v1beta1 "github.com/vmware-tanzu/antrea/pkg/apis/networkpolicy/v1beta1"
	scheme "github.com/vmware-tanzu/antrea/pkg/client/clientset/versioned/scheme"
	v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	watch "k8s.io/apimachinery/pkg/watch"
	rest "k8s.io/client-go/rest"
)

// NetworkPoliciesGetter has a method to return a NetworkPolicyInterface.
// A group's client should implement this interface.
type NetworkPoliciesGetter interface {
	NetworkPolicies(namespace string) NetworkPolicyInterface
}

// NetworkPolicyInterface has methods to work with NetworkPolicy resources.
type NetworkPolicyInterface interface {
	Get(name string, options v1.GetOptions) (*v1beta1.NetworkPolicy, error)
	List(opts v1.ListOptions) (*v1beta1.NetworkPolicyList, error)
	Watch(opts v1.ListOptions) (watch.Interface, error)
	NetworkPolicyExpansion
}

// networkPolicies implements NetworkPolicyInterface
type networkPolicies struct {
	client rest.Interface
	ns     string
}

// newNetworkPolicies returns a NetworkPolicies
func newNetworkPolicies(c *NetworkpolicyV1beta1Client, namespace string) *networkPolicies {
	return &networkPolicies{
		client: c.RESTClient(),
		ns:     namespace,
	}
}

// Get takes name of the networkPolicy, and returns the corresponding networkPolicy object, and an error if there is any.
func (c *networkPolicies) Get(name string, options v1.GetOptions) (result *v1beta1.NetworkPolicy, err error) {
	result = &v1beta1.NetworkPolicy{}
	err = c.client.Get().
		Namespace(c.ns).
		Resource("networkpolicies").
		Name(name).
		VersionedParams(&options, scheme.ParameterCodec).
		Do().
		Into(result)
	return
}

// List takes label and field selectors, and returns the list of NetworkPolicies that match those selectors.
func (c *networkPolicies) List(opts v1.ListOptions) (result *v1beta1.NetworkPolicyList, err error) {
	var timeout time.Duration
	if opts.TimeoutSeconds != nil {
		timeout = time.Duration(*opts.TimeoutSeconds) * time.Second
	}
	result = &v1beta1.NetworkPolicyList{}
	err = c.client.Get().
		Namespace(c.ns).
		Resource("networkpolicies").
		VersionedParams(&opts, scheme.ParameterCodec).
		Timeout(timeout).
		Do().
		Into(result)
	return
}

// Watch returns a watch.Interface that watches the requested networkPolicies.
func (c *networkPolicies) Watch(opts v1.ListOptions) (watch.Interface, error) {
	var timeout time.Duration
	if opts.TimeoutSeconds != nil {
		timeout = time.Duration(*opts.TimeoutSeconds) * time.Second
	}
	opts.Watch = true
	return c.client.Get().
		Namespace(c.ns).
		Resource("networkpolicies").
		VersionedParams(&opts, scheme.ParameterCodec).
		Timeout(timeout).
		Watch()
}
