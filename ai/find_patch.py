
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: python find_patch.py <PR_NUMBER>")
    sys.exit(1)

pr_number = sys.argv[1]

try:
    git_command = f'git fetch origin pull/{pr_number}/head:pr-{pr_number} && git checkout pr-{pr_number}'
    subprocess.run(git_command, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error: Unable to fetch or checkout PR-{pr_number}")
    sys.exit(1)

try:
    git_diff_command = 'git show HEAD'
    diff_output_bytes = subprocess.check_output(git_diff_command, shell=True)
    diff_output = diff_output_bytes.decode('utf-8')
    print(f"Diff for PR-{pr_number}:\n")
    print(diff_output)
except subprocess.CalledProcessError as e:
    print(f"Error: Unable to retrieve diff for PR-{pr_number}")
    sys.exit(1)

try:
    git_checkout_main = f'git checkout main && git branch -D pr-{pr_number}'
    subprocess.run(git_checkout_main, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print("Error: Unable to return to the main branch")
