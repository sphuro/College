import os
import sys
import time
import hashlib
import requests

# Configuration - Replace with your own API key and secret
API_KEY = '641028012d3811da64073628eb0f4f2dab6eee2e'  # Replace with your API key
API_SECRET = '06d53e03116de50c89c2cafca4f451d34ad047a5'  # Replace with your API secret
USER_HANDLE = 'us3r'  # Replace with your Codeforces handle
API_BASE_URL = 'https://codeforces.com/api'

def generate_api_sig(method, params, secret):
    sorted_params = '&'.join(f'{k}={v}' for k, v in sorted(params.items()))
    signature = f'123456/{method}?{sorted_params}#{secret}'
    hash_digest = hashlib.sha512(signature.encode()).hexdigest()
    return f'123456{hash_digest}'

# Function to fetch user information
def fetch_user_info(handle):
    params = {'handles': handle, 'apiKey': API_KEY, 'time': int(time.time())}
    sig = generate_api_sig('user.info', params, API_SECRET)
    params['apiSig'] = sig
    response = requests.get(f'{API_BASE_URL}/user.info', params=params)
    data = response.json()
    if data['status'] == 'OK':
        return data['result'][0]
    else:
        raise Exception('Failed to fetch user info: ' + data.get('comment', 'Unknown error'))

# Function to fetch contest details by contest ID
def fetch_contest_details(contest_id=None):
    params = {'apiKey': API_KEY, 'time': int(time.time())}
    sig = generate_api_sig('contest.list', params, API_SECRET)
    params['apiSig'] = sig
    response = requests.get(f'{API_BASE_URL}/contest.list', params=params)
    data = response.json()
    if data['status'] == 'OK':
        contests = data['result']
        if contest_id:
            for contest in contests:
                if contest['id'] == contest_id:
                    return contest
            raise Exception(f'Contest ID {contest_id} not found.')
        return contests
    else:
        raise Exception('Failed to fetch contests: ' + data.get('comment', 'Unknown error'))

# Function to create contest directory
def create_contest_directory(contest_id):
    directory = f'Contest_{contest_id}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# Function to create C++ files for problems
def create_cpp_files(contest_directory, problems):
    for problem in problems:
        problem_id = problem['index']
        filename = os.path.join(contest_directory, f'{problem_id}.cpp')
        with open(filename, 'w') as file:
            file.write('// Problem: ' + problem['name'] + '\n')
            file.write('#include <iostream>\n')
            file.write('using namespace std;\n')
            file.write('int main() {\n')
            file.write('    // TODO: Implement the solution\n')
            file.write('    return 0;\n')
            file.write('}\n')

# Function to fetch problems within a rating range
def fetch_problems_by_rating(min_rating, max_rating):
    params = {'apiKey': API_KEY, 'time': int(time.time())}
    sig = generate_api_sig('problemset.problems', params, API_SECRET)
    params['apiSig'] = sig
    response = requests.get(f'{API_BASE_URL}/problemset.problems', params=params)
    data = response.json()
    if data['status'] == 'OK':
        problems = data['result']['problems']
        filtered_problems = [p for p in problems if 'rating' in p and min_rating <= p['rating'] <= max_rating]
        return filtered_problems
    else:
        raise Exception('Failed to fetch problems: ' + data.get('comment', 'Unknown error'))

# Function to fetch the problem statement and test cases
def fetch_problem_details(problem):
    # Mock data to simulate the process
    # Normally, you would scrape the problem page here
    statement = f"This is a mock statement for problem {problem['name']}."
    test_cases = [
        {"input": "1\n2\n", "output": "3\n"},
        {"input": "2\n3\n", "output": "5\n"}
    ]
    return statement, test_cases

# Function to create a problem directory and file
def create_problem_directory(problem):
    directory = f'Problem_{problem["contestId"]}_{problem["index"]}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, 'problem.txt')

    # Fetch problem details
    statement, test_cases = fetch_problem_details(problem)

    with open(filename, 'w') as file:
        file.write(f'Problem: {problem["name"]}\n')
        file.write(f'Contest ID: {problem["contestId"]}\n')
        file.write(f'Index: {problem["index"]}\n')
        file.write(f'Rating: {problem.get("ratiNG", "Not Rated")}\n\n')
        file.write("Problem Statement:\n")
        file.write(statement + "\n\n")
        file.write("Test Cases:\n")
        for i, case in enumerate(test_cases):
            file.write(f"Test Case {i+1}:\n")
            file.write("Input:\n" + case["input"] + "\n")
            file.write("Output:\n" + case["output"] + "\n")
            file.write("\n")
    return directory

# Main function
def main():
    if len(sys.argv) < 2:
        print("Usage: python file.py [option] [parameters]")
        sys.exit(1)

    option = sys.argv[1]

    try:
        if option == '--r':
            user_info = fetch_user_info(USER_HANDLE)
            print(f'User Rating: {user_info.get("rating", "Not Rated")}')

        elif option == '--f':
            user_info = fetch_user_info(USER_HANDLE)
            friends = user_info.get('friendsOfCount', 'N/A')
            print(f'Number of Friends: {friends}')

        elif option == '--fc':
            contests = fetch_contest_details()
            future_contests = [contest for contest in contests if contest['phase'] == 'BEFORE']
            for contest in future_contests:
                print(f'{contest["id"]}: {contest["name"]} - {contest["startTimeSeconds"]}')

        elif option == '--c':
            if len(sys.argv) != 3:
                print("Usage: python file.py --c <contest_id>")
                sys.exit(1)
            contest_id = int(sys.argv[2])
            contest = fetch_contest_details(contest_id)
            contest_directory = create_contest_directory(contest['id'])
            print(f'Created directory: {contest_directory}')

            # Fetch problems for the specific contest
            problems = [{'index': chr(65 + i), 'name': f'Problem {chr(65 + i)}'} for i in range(5)]  # Mock data

            # Create CPP files
            create_cpp_files(contest_directory, problems)
            print(f'Created {len(problems)} C++ files in {contest_directory}')

        elif option == '--pr':
            if len(sys.argv) == 4:  # Range of ratings
                min_rating = int(sys.argv[2])
                max_rating = int(sys.argv[3])
                problems = fetch_problems_by_rating(min_rating, max_rating)
                for problem in problems:
                    print(f'{problem["contestId"]}-{problem["index"]}: {problem["name"]} - Rating: {problem.get("rating", "Not Rated")}')
            elif len(sys.argv) == 3:  # Specific problem
                problem_id = sys.argv[2]
                problems = fetch_problems_by_rating(800, 3500)  # Fetch all problems
                for problem in problems:
                    if problem['contestId'] == int(problem_id.split('-')[0]) and problem['index'] == problem_id.split('-')[1]:
                        directory = create_problem_directory(problem)
                        print(f'Created directory and problem.txt for {problem["name"]} in {directory}')
                        break
                else:
                    print(f'Problem {problem_id} not found.')

        else:
            print("Invalid option. Available options: --r, --f, --fc, --c, --pr")
            sys.exit(1)

    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()

