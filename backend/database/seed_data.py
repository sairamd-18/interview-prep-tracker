"""
Comprehensive seed data generator for the Agentic AI Interview Preparation Tracker.
Populates subjects, topics, quiz questions, coding problems, and demo user data.
"""
import json
from datetime import datetime, timedelta
from backend.database.db import get_db, init_db
from backend.auth_utils import hash_password

def seed():
    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) as count FROM subjects")
        if cursor.fetchone()["count"] > 0:
            print("Database already contains data. Skipping subject/problem reseed.")
            return

        print("Seeding subjects and topics...")
        # 1. Subjects & Topics
        subjects_data = [
            {
                "name": "Data Structures & Algorithms",
                "code": "DSA",
                "description": "Core algorithms, data structures, space/time complexity, and problem-solving techniques.",
                "icon": "Code2",
                "order": 1,
                "topics": [
                    ("Arrays & Strings", "Linear collections, two-pointers, sliding window", 1.0),
                    ("Linked Lists", "Singly, doubly, circular lists, pointer manipulation", 1.0),
                    ("Stacks & Queues", "LIFO/FIFO structures, monotonic stacks", 1.0),
                    ("Trees & Binary Search Trees", "Tree traversals, height, LCA, BST properties", 1.2),
                    ("Graphs & Traversals", "BFS, DFS, shortest path algorithms (Dijkstra, Bellman-Ford)", 1.4),
                    ("Dynamic Programming", "Memoization, tabulation, optimal substructure, knapsack, LCS", 1.6),
                    ("Sorting & Searching", "QuickSort, MergeSort, Binary Search variations", 1.0)
                ]
            },
            {
                "name": "Database Management Systems",
                "code": "DBMS",
                "description": "Relational algebra, SQL, normalization, ACID properties, indexing and transactions.",
                "icon": "Database",
                "order": 2,
                "topics": [
                    ("SQL Queries & Joins", "SELECT, GROUP BY, HAVING, INNER/LEFT/RIGHT/CROSS joins", 1.0),
                    ("Normalization & ER Modeling", "1NF, 2NF, 3NF, BCNF, functional dependencies", 1.2),
                    ("Transactions & Concurrency", "ACID properties, serializability, 2PL, isolation levels", 1.4),
                    ("Indexing & Query Optimization", "B-Trees, B+ Trees, Hash indexes, execution plans", 1.3),
                    ("NoSQL & Distributed DBs", "CAP theorem, document stores, key-value stores", 1.1)
                ]
            },
            {
                "name": "Operating Systems",
                "code": "OS",
                "description": "Process management, concurrency, CPU scheduling, deadlocks, and virtual memory.",
                "icon": "Cpu",
                "order": 3,
                "topics": [
                    ("Processes & Threads", "PCB, context switching, multithreading, fork/exec", 1.0),
                    ("CPU Scheduling", "FCFS, SJF, Round Robin, priority scheduling", 1.1),
                    ("Process Synchronization", "Semaphores, mutexes, critical section, dining philosophers", 1.4),
                    ("Deadlocks", "Coffman conditions, Banker's algorithm, prevention & detection", 1.3),
                    ("Memory Management & Paging", "Virtual memory, TLB, page replacement (LRU, FIFO)", 1.3)
                ]
            },
            {
                "name": "Computer Networks",
                "code": "CN",
                "description": "Network architectures, protocols, routing algorithms, transport layer, and security.",
                "icon": "Network",
                "order": 4,
                "topics": [
                    ("OSI & TCP/IP Models", "Layers, encapsulation, responsibilities", 1.0),
                    ("Transport Layer (TCP vs UDP)", "3-way handshake, flow control, congestion control", 1.3),
                    ("Network Layer & Routing", "IP addressing, CIDR subnetting, OSPF, BGP, ARP", 1.3),
                    ("Application Protocols", "HTTP/HTTPS, DNS, FTP, SMTP, WebSockets", 1.1),
                    ("Network Security", "Firewalls, TLS/SSL handshake, symmetric vs asymmetric encryption", 1.2)
                ]
            },
            {
                "name": "Object-Oriented Programming",
                "code": "OOP",
                "description": "Core paradigms, inheritance, polymorphism, design patterns, and SOLID principles.",
                "icon": "Boxes",
                "order": 5,
                "topics": [
                    ("Core OOP Concepts", "Abstraction, Encapsulation, Inheritance, Polymorphism", 1.0),
                    ("Design Patterns", "Singleton, Factory, Observer, Strategy, Decorator", 1.4),
                    ("SOLID Principles", "Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion", 1.3)
                ]
            },
            {
                "name": "Quantitative & Logical Aptitude",
                "code": "APT",
                "description": "Number theory, probability, permutations, data interpretation, and deductive reasoning.",
                "icon": "Calculator",
                "order": 6,
                "topics": [
                    ("Quantitative Ability", "Percentages, profit/loss, time & work, speed & distance", 1.0),
                    ("Probability & Combinatorics", "Permutations, combinations, conditional probability", 1.2),
                    ("Logical Reasoning", "Syllogisms, blood relations, seating arrangements, series", 1.1)
                ]
            },
            {
                "name": "Behavioral & HR",
                "code": "BEH",
                "description": "STAR method responses, leadership, conflict resolution, career aspirations.",
                "icon": "Users",
                "order": 7,
                "topics": [
                    ("STAR Methodology", "Situation, Task, Action, Result framing", 1.0),
                    ("Conflict & Collaboration", "Handling disagreements, team dynamics, feedback", 1.1),
                    ("Leadership & Problem Solving", "Ownership, failure handling, project delivery under pressure", 1.2)
                ]
            }
        ]

        topic_map = {} # (subject_code, topic_name) -> topic_id
        for subj in subjects_data:
            cursor.execute(
                "INSERT INTO subjects (name, code, description, icon, display_order) VALUES (?, ?, ?, ?, ?)",
                (subj["name"], subj["code"], subj["description"], subj["icon"], subj["order"])
            )
            subj_id = cursor.lastrowid
            for t_name, t_desc, t_weight in subj["topics"]:
                cursor.execute(
                    "INSERT INTO topics (subject_id, name, description, difficulty_weight) VALUES (?, ?, ?, ?)",
                    (subj_id, t_name, t_desc, t_weight)
                )
                topic_map[(subj["code"], t_name)] = cursor.lastrowid

        print("Seeding quiz questions...")
        # 2. Quiz Questions
        questions_pool = [
            # Dynamic Programming
            (
                "DSA", "Dynamic Programming",
                "What is the primary condition required to apply Dynamic Programming to an optimization problem?",
                ["Greedy choice property and disjoint subproblems", "Optimal substructure and overlapping subproblems", "Divide and conquer with independent subproblems", "Sorted input and constant space"],
                1,
                "Dynamic programming requires two main properties: optimal substructure (an optimal solution contains optimal solutions to subproblems) and overlapping subproblems.",
                "Medium"
            ),
            (
                "DSA", "Dynamic Programming",
                "What is the time complexity of solving the 0/1 Knapsack problem using Dynamic Programming with N items and capacity W?",
                ["O(N log N)", "O(2^N)", "O(N * W)", "O(W^2)"],
                2,
                "The pseudo-polynomial DP approach uses a table of size (N+1) x (W+1), resulting in O(N*W) time and space complexity.",
                "Medium"
            ),
            (
                "DSA", "Dynamic Programming",
                "In the Longest Common Subsequence (LCS) problem of two strings of length m and n, what is the recurrence relation when characters match (X[i-1] == Y[j-1])?",
                ["LCS[i][j] = 1 + LCS[i-1][j-1]", "LCS[i][j] = max(LCS[i-1][j], LCS[i][j-1])", "LCS[i][j] = LCS[i-1][j-1]", "LCS[i][j] = 1 + max(LCS[i-1][j], LCS[i][j-1])"],
                0,
                "When characters match at indices i-1 and j-1, they contribute 1 to the subsequence length: 1 + LCS[i-1][j-1].",
                "Hard"
            ),
            (
                "DSA", "Dynamic Programming",
                "Which approach computes subproblem solutions from base cases upwards to the final answer?",
                ["Memoization (Top-down)", "Tabulation (Bottom-up)", "Branch and Bound", "Recursive Backtracking"],
                1,
                "Tabulation iteratively fills an array or table starting from the smallest base cases up to the target value.",
                "Easy"
            ),

            # Arrays & Strings
            (
                "DSA", "Arrays & Strings",
                "What is the optimal time complexity to find the maximum sum contiguous subarray (Kadane's Algorithm)?",
                ["O(N^2)", "O(N log N)", "O(N)", "O(1)"],
                2,
                "Kadane's Algorithm scans the array once maintaining current maximum and global maximum in linear O(N) time.",
                "Easy"
            ),
            (
                "DSA", "Arrays & Strings",
                "Which technique is most suitable for finding the longest substring without repeating characters?",
                ["Binary Search", "Sliding Window with Hash Map", "Monotonic Stack", "Depth First Search"],
                1,
                "A sliding window with two pointers and a character frequency map finds the optimal substring in O(N) time.",
                "Medium"
            ),

            # Trees & BST
            (
                "DSA", "Trees & Binary Search Trees",
                "Which traversal of a Binary Search Tree produces nodes in non-decreasing sorted order?",
                ["Preorder", "Inorder", "Postorder", "Level-order"],
                1,
                "Inorder traversal visits left child, root, then right child, which strictly produces sorted order in a BST.",
                "Easy"
            ),
            (
                "DSA", "Trees & Binary Search Trees",
                "What is the worst-case time complexity of searching in an unbalanced Binary Search Tree?",
                ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
                2,
                "In a degenerate (skewed) tree, the tree behaves like a linked list, degrading search time to O(N).",
                "Medium"
            ),

            # Graphs
            (
                "DSA", "Graphs & Traversals",
                "Which algorithm is used to find the shortest path in a weighted graph with non-negative edge weights?",
                ["Prim's Algorithm", "Dijkstra's Algorithm", "Kruskal's Algorithm", "Floyd-Warshall Algorithm"],
                1,
                "Dijkstra's algorithm efficiently computes single-source shortest paths for non-negative weights using a min-priority queue in O((V + E) log V).",
                "Medium"
            ),
            (
                "DSA", "Graphs & Traversals",
                "Which data structure is fundamentally used in Breadth-First Search (BFS)?",
                ["Stack", "Queue", "Max-Heap", "Set"],
                1,
                "BFS explores vertices level by level using a FIFO Queue.",
                "Easy"
            ),

            # DBMS - SQL Queries & Joins
            (
                "DBMS", "SQL Queries & Joins",
                "Which SQL clause is used to filter rows AFTER an aggregate function has been computed?",
                ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
                1,
                "WHERE filters rows prior to aggregation, whereas HAVING filters aggregated groups.",
                "Easy"
            ),
            (
                "DBMS", "SQL Queries & Joins",
                "What does a FULL OUTER JOIN return?",
                ["Only matching rows from both tables", "All rows from the left table and matched from right", "All rows when there is a match in either left or right table", "Cartesian product of both tables"],
                2,
                "FULL OUTER JOIN combines the results of both LEFT and RIGHT outer joins, returning all rows with NULLs where no match exists.",
                "Medium"
            ),

            # DBMS - Transactions
            (
                "DBMS", "Transactions & Concurrency",
                "What does the 'I' in ACID properties stand for?",
                ["Integrity", "Isolation", "Indexing", "Inheritance"],
                1,
                "Isolation ensures that concurrent transactions execute independently without interfering with each other.",
                "Easy"
            ),
            (
                "DBMS", "Transactions & Concurrency",
                "Which anomaly occurs when a transaction reads data that has been modified by another uncommitted transaction?",
                ["Phantom Read", "Non-repeatable Read", "Dirty Read", "Lost Update"],
                2,
                "A Dirty Read occurs when transaction T1 reads data written by uncommitted transaction T2 that is subsequently rolled back.",
                "Medium"
            ),

            # OS - Processes & Threads
            (
                "OS", "Processes & Threads",
                "What resource is NOT shared between threads of the same process?",
                ["Address space", "Open file descriptors", "Global variables", "Stack and register state"],
                3,
                "Each thread has its own private program counter, register state, and stack to maintain its execution context.",
                "Medium"
            ),
            (
                "OS", "Processes & Threads",
                "What is a context switch?",
                ["Switching between user mode and kernel mode", "Saving state of an active process and loading state of another process", "Changing priority of a thread", "Swapping memory from RAM to disk"],
                1,
                "A context switch stores the current state (registers, PC) of the running process in its PCB and restores another scheduled process.",
                "Easy"
            ),

            # OS - Deadlocks
            (
                "OS", "Deadlocks",
                "Which of the following is NOT one of the four Coffman conditions for deadlock?",
                ["Mutual Exclusion", "Preemption allowed", "Hold and Wait", "Circular Wait"],
                1,
                "The condition is 'No Preemption'. If preemption is allowed, deadlocks cannot occur.",
                "Medium"
            ),
            (
                "OS", "Deadlocks",
                "Which algorithm is used for deadlock avoidance by verifying safe state transitions?",
                ["Round Robin", "Banker's Algorithm", "Bakery Algorithm", "Dekker's Algorithm"],
                1,
                "Dijkstra's Banker's Algorithm evaluates resource requests to guarantee the system never enters an unsafe state.",
                "Medium"
            ),

            # Computer Networks - Transport Layer
            (
                "CN", "Transport Layer (TCP vs UDP)",
                "How many packets are exchanged in a standard TCP connection teardown (termination)?",
                ["2 packets", "3 packets", "4 packets (FIN, ACK, FIN, ACK)", "1 packet"],
                2,
                "TCP teardown typically uses a 4-way handshake: FIN -> ACK, followed by FIN -> ACK in the reverse direction.",
                "Medium"
            ),
            (
                "CN", "Transport Layer (TCP vs UDP)",
                "Which protocol is connectionless, does not guarantee delivery, and has minimal header overhead?",
                ["TCP", "UDP", "SCTP", "BGP"],
                1,
                "UDP (User Datagram Protocol) provides low-latency, connectionless, best-effort datagram delivery with only an 8-byte header.",
                "Easy"
            ),
            (
                "CN", "OSI & TCP/IP Models",
                "At which OSI layer does IP routing operate?",
                ["Data Link Layer (Layer 2)", "Network Layer (Layer 3)", "Transport Layer (Layer 4)", "Session Layer (Layer 5)"],
                1,
                "The Network Layer is responsible for logical addressing (IP addresses) and packet routing across networks.",
                "Easy"
            ),

            # OOP - Core Concepts & Design Patterns
            (
                "OOP", "Core OOP Concepts",
                "What is the ability of an object to take on many forms or execute different methods via the same interface?",
                ["Encapsulation", "Polymorphism", "Abstraction", "Coupling"],
                1,
                "Polymorphism allows objects of different classes to respond to the same interface or method call appropriately.",
                "Easy"
            ),
            (
                "OOP", "Design Patterns",
                "Which design pattern ensures that a class has only one instance and provides a global access point to it?",
                ["Factory Pattern", "Singleton Pattern", "Observer Pattern", "Adapter Pattern"],
                1,
                "The Singleton Pattern restricts instantiation of a class to a single object with lazy initialization.",
                "Easy"
            ),
            (
                "OOP", "SOLID Principles",
                "What does the 'L' in SOLID principles represent?",
                ["Linear Scalability", "Liskov Substitution Principle", "Loose Coupling", "Lazy Evaluation"],
                1,
                "Liskov Substitution Principle states that derived classes must be substitutable for their base classes without altering program correctness.",
                "Medium"
            ),

            # Aptitude
            (
                "APT", "Quantitative Ability",
                "If A can complete a work in 10 days and B can complete it in 15 days, in how many days can they complete it working together?",
                ["5 days", "6 days", "8 days", "12 days"],
                1,
                "1/10 + 1/15 = (3 + 2)/30 = 5/30 = 1/6 work per day, so together they take 6 days.",
                "Easy"
            ),
            (
                "APT", "Probability & Combinatorics",
                "Two fair dice are rolled. What is the probability that the sum of the numbers is equal to 7?",
                ["1/12", "1/6", "5/36", "7/36"],
                1,
                "Favorable outcomes: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 outcomes out of 36 total, which simplifies to 6/36 = 1/6.",
                "Medium"
            ),

            # Behavioral
            (
                "BEH", "STAR Methodology",
                "In the STAR technique for answering behavioral questions, what does the 'A' stand for?",
                ["Assessment", "Action", "Achievement", "Adaptation"],
                1,
                "STAR stands for Situation, Task, Action, and Result. 'Action' details the specific steps you personally took.",
                "Easy"
            ),
            (
                "BEH", "Conflict & Collaboration",
                "When receiving critical feedback from a senior engineer during a code review, what is the most professional response?",
                ["Argue immediately that your solution is faster", "Ignore the comments and merge the PR", "Listen with an open mind, ask clarifying questions, and discuss trade-offs constructively", "Escalate to the engineering manager immediately"],
                2,
                "Constructive receipt of code review feedback promotes collaboration, code quality, and professional growth.",
                "Easy"
            )
        ]

        for subj_code, topic_name, q_text, opts, correct_idx, expl, diff in questions_pool:
            t_id = topic_map.get((subj_code, topic_name))
            if t_id:
                cursor.execute(
                    """INSERT INTO questions (topic_id, question_text, options_json, correct_answer, explanation, difficulty)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (t_id, q_text, json.dumps(opts), correct_idx, expl, diff)
                )

        print("Seeding coding problems...")
        # 3. Coding Problems
        coding_problems = [
            (
                "DSA", "Arrays & Strings",
                "Two Sum",
                "two-sum",
                "Easy",
                "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. You may assume each input would have exactly one solution, and you may not use the same element twice.",
                "def two_sum(nums: list[int], target: int) -> list[int]:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "nums = [2,7,11,15], target = 9", "expected": "[0, 1]"},
                    {"input": "nums = [3,2,4], target = 6", "expected": "[1, 2]"},
                    {"input": "nums = [3,3], target = 6", "expected": "[0, 1]"}
                ]),
                "Use a hash map to store complements (target - num). Time: O(N), Space: O(N).",
                82.4
            ),
            (
                "DSA", "Arrays & Strings",
                "Longest Substring Without Repeating Characters",
                "longest-substring-without-repeating-characters",
                "Medium",
                "Given a string `s`, find the length of the longest substring without repeating characters.",
                "def length_of_longest_substring(s: str) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "s = 'abcabcbb'", "expected": "3"},
                    {"input": "s = 'bbbbb'", "expected": "1"},
                    {"input": "s = 'pwwkew'", "expected": "3"}
                ]),
                "Sliding window using a hash map to track last seen indices of characters.",
                54.8
            ),
            (
                "DSA", "Dynamic Programming",
                "Climbing Stairs",
                "climbing-stairs",
                "Easy",
                "You are climbing a staircase. It takes `n` steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
                "def climb_stairs(n: int) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "n = 2", "expected": "2"},
                    {"input": "n = 3", "expected": "3"},
                    {"input": "n = 5", "expected": "8"}
                ]),
                "Fibonacci sequence recurrence: dp[i] = dp[i-1] + dp[i-2] with dp[1]=1, dp[2]=2.",
                76.2
            ),
            (
                "DSA", "Dynamic Programming",
                "Coin Change",
                "coin-change",
                "Medium",
                "You are given an integer array `coins` representing coins of different denominations and an integer `amount`. Return the fewest number of coins that you need to make up that amount. If that amount cannot be made up, return -1.",
                "def coin_change(coins: list[int], amount: int) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "coins = [1,2,5], amount = 11", "expected": "3"},
                    {"input": "coins = [2], amount = 3", "expected": "-1"},
                    {"input": "coins = [1], amount = 0", "expected": "0"}
                ]),
                "Unbounded knapsack DP: dp[i] = min(dp[i], 1 + dp[i - c]) for all c in coins.",
                46.3
            ),
            (
                "DSA", "Dynamic Programming",
                "0/1 Knapsack Problem",
                "zero-one-knapsack",
                "Medium",
                "Given weights and values of `n` items, put these items in a knapsack of capacity `W` to get the maximum total value in the knapsack. Each item can either be chosen or left behind.",
                "def knapsack(weights: list[int], values: list[int], W: int) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "weights = [1,3,4,5], values = [1,4,5,7], W = 7", "expected": "9"},
                    {"input": "weights = [2,2,4,5], values = [3,4,5,6], W = 3", "expected": "4"}
                ]),
                "2D DP table where dp[i][w] = max(dp[i-1][w], values[i-1] + dp[i-1][w-weights[i-1]]).",
                48.1
            ),
            (
                "DSA", "Dynamic Programming",
                "Longest Increasing Subsequence",
                "longest-increasing-subsequence",
                "Medium",
                "Given an integer array `nums`, return the length of the longest strictly increasing subsequence.",
                "def length_of_lis(nums: list[int]) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "nums = [10,9,2,5,3,7,101,18]", "expected": "4"},
                    {"input": "nums = [0,1,0,3,2,3]", "expected": "4"},
                    {"input": "nums = [7,7,7,7,7,7,7]", "expected": "1"}
                ]),
                "DP in O(N^2) or Patience Sorting + Binary Search in O(N log N).",
                52.6
            ),
            (
                "DSA", "Linked Lists",
                "Reverse a Linked List",
                "reverse-linked-list",
                "Easy",
                "Given the `head` of a singly linked list, reverse the list, and return the reversed list.",
                "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head: ListNode) -> ListNode:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "head = [1,2,3,4,5]", "expected": "[5,4,3,2,1]"},
                    {"input": "head = [1,2]", "expected": "[2,1]"}
                ]),
                "Iterate through the list reversing pointers using prev, curr, next pointers.",
                78.5
            ),
            (
                "DSA", "Trees & Binary Search Trees",
                "Maximum Depth of Binary Tree",
                "maximum-depth-of-binary-tree",
                "Easy",
                "Given the `root` of a binary tree, return its maximum depth (number of nodes along the longest path from the root down to the farthest leaf node).",
                "def max_depth(root) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "root = [3,9,20,null,null,15,7]", "expected": "3"},
                    {"input": "root = [1,null,2]", "expected": "2"}
                ]),
                "Recursive postorder: 1 + max(max_depth(root.left), max_depth(root.right)).",
                75.1
            ),
            (
                "DSA", "Graphs & Traversals",
                "Number of Islands",
                "number-of-islands",
                "Medium",
                "Given an `m x n` 2D binary grid `grid` which represents a map of '1's (land) and '0's (water), return the number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.",
                "def num_islands(grid: list[list[str]]) -> int:\n    # Write your solution here\n    pass",
                json.dumps([
                    {"input": "grid = [['1','1','0'],['1','1','0'],['0','0','1']]", "expected": "2"},
                    {"input": "grid = [['1','0'],['0','1']]", "expected": "2"}
                ]),
                "Standard BFS or DFS marking visited land cells as '0' to avoid duplicates.",
                58.4
            ),
            (
                "DBMS", "SQL Queries & Joins",
                "Second Highest Salary",
                "second-highest-salary",
                "Medium",
                "Write an SQL query to report the second highest distinct salary from the `Employee` table. If there is no second highest salary, return NULL.",
                "SELECT MAX(salary) AS SecondHighestSalary\nFROM Employee\nWHERE salary < (SELECT MAX(salary) FROM Employee);",
                json.dumps([
                    {"input": "Employee = [[1, 100], [2, 200], [3, 300]]", "expected": "200"}
                ]),
                "Can be solved using subquery with MAX() or DENSE_RANK() window function.",
                42.9
            )
        ]

        for subj_code, topic_name, title, slug, diff, desc, starter, tests, sol, acc in coding_problems:
            t_id = topic_map.get((subj_code, topic_name))
            if t_id:
                cursor.execute(
                    """INSERT INTO coding_problems (topic_id, title, slug, difficulty, description, starter_code, test_cases_json, solution_notes, acceptance_rate)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (t_id, title, slug, diff, desc, starter, tests, sol, acc)
                )

        print("Seeding demo user, profiles, and initial activity...")
        # 4. Demo User
        pwd_hash = hash_password("password123")
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("demo@example.com", pwd_hash, "Alex Mercer", "student")
        )
        user_id = cursor.lastrowid

        interview_date = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
        cursor.execute(
            """INSERT INTO user_profiles (user_id, target_role, target_company, interview_date, daily_study_hours, experience_level, bio)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "Software Development Engineer (SDE)", "Google / Tier 1 Tech", interview_date, 3.5, "Final Year CS Student", "Prepping for upcoming campus placements.")
        )

        # 5. Populate Initial Skill Profiles across topics (Making Dynamic Programming explicitly WEAK)
        cursor.execute("SELECT id, subject_id, name FROM topics")
        all_topics = cursor.fetchall()
        
        for top in all_topics:
            t_name = top["name"]
            # Default profiles
            if "Dynamic Programming" in t_name:
                score = 35.0
                status = "Weak"
                quizzes = 2
            elif "Computer Networks" in t_name or "OSI" in t_name or "Transport Layer" in t_name:
                score = 45.0
                status = "Weak"
                quizzes = 1
            elif "Array" in t_name or "Linked" in t_name or "SQL" in t_name:
                score = 85.0
                status = "Strong"
                quizzes = 4
            elif "Tree" in t_name or "Graph" in t_name:
                score = 65.0
                status = "Moderate"
                quizzes = 2
            else:
                score = 70.0
                status = "Moderate"
                quizzes = 1

            cursor.execute(
                """INSERT INTO skill_profiles (user_id, subject_id, topic_id, proficiency_score, status, confidence_level, quizzes_taken)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, top["subject_id"], top["id"], score, status, 0.7, quizzes)
            )

        # 6. Active Study Plan
        cursor.execute(
            """INSERT INTO study_plans (user_id, title, target_date, total_weeks, current_status, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, "4-Week Placement Sprint: SDE Role", interview_date, 4, "Active", "Adaptive schedule dynamically prioritizing Dynamic Programming & Computer Networks.")
        )
        plan_id = cursor.lastrowid

        # 7. Initial Study Tasks
        dp_topic_id = topic_map.get(("DSA", "Dynamic Programming"))
        array_topic_id = topic_map.get(("DSA", "Arrays & Strings"))
        cn_topic_id = topic_map.get(("CN", "Transport Layer (TCP vs UDP)"))

        tasks = [
            (plan_id, user_id, dp_topic_id, "Master 1D Dynamic Programming Foundations", "Review Climbing Stairs, House Robber, and memoization patterns.", "High", 90, 1, 1),
            (plan_id, user_id, dp_topic_id, "Solve Coin Change & 0/1 Knapsack", "Practice unbounded vs 0/1 knapsack tabulations.", "High", 120, 2, 0),
            (plan_id, user_id, cn_topic_id, "Revise TCP 3-Way Handshake & Flow Control", "Study TCP vs UDP headers, congestion window algorithms.", "High", 60, 3, 0),
            (plan_id, user_id, array_topic_id, "Two Pointers & Sliding Window Practice", "Solve 3 medium difficulty LeetCode problems.", "Medium", 60, 4, 1),
            (plan_id, user_id, dp_topic_id, "Longest Common Subsequence & Edit Distance", "Master string DP tabular transitions.", "High", 90, 5, 0),
        ]
        for t in tasks:
            cursor.execute(
                """INSERT INTO study_tasks (study_plan_id, user_id, topic_id, title, description, priority, estimated_minutes, day_number, is_completed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                t
            )

        # 8. Sample Coding Submissions
        cursor.execute("SELECT id, title FROM coding_problems WHERE slug = 'two-sum'")
        p_two_sum = cursor.fetchone()
        if p_two_sum:
            cursor.execute(
                """INSERT INTO coding_submissions (user_id, problem_id, code, language, status, execution_time_ms, feedback)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, p_two_sum["id"], "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i", "python", "Accepted", 42, "Optimal O(N) single pass solution!")
            )

        cursor.execute("SELECT id, title FROM coding_problems WHERE slug = 'climbing-stairs'")
        p_stairs = cursor.fetchone()
        if p_stairs:
            cursor.execute(
                """INSERT INTO coding_submissions (user_id, problem_id, code, language, status, execution_time_ms, feedback)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, p_stairs["id"], "def climb_stairs(n):\n    if n <= 2: return n\n    a, b = 1, 2\n    for _ in range(3, n+1):\n        a, b = b, a + b\n    return b", "python", "Accepted", 38, "Optimal O(N) time and O(1) space solution.")
            )

        # 9. Initial Resume and Analysis
        sample_resume_text = """
Alex Mercer
Email: alex.mercer@example.com | Phone: +1-555-0199 | GitHub: github.com/alexmercer
Education: B.Tech in Computer Science and Engineering, CGPA: 8.8 / 10.0 (Graduating May 2026)

Technical Skills:
Languages: Python, Java, C++, JavaScript, SQL
Frameworks & Tools: React.js, Node.js, FastAPI, Git, Docker, SQLite, PostgreSQL
Core CS: Data Structures, Algorithms, DBMS, Object-Oriented Design

Projects:
1. Collaborative Code Editor
- Built a real-time collaborative code editor using WebSockets and React.
- Implemented operational transformation algorithms ensuring seamless synchronization for 50+ concurrent users.
- Containerized frontend and backend services using Docker.

2. Distributed File Storage Cache
- Developed an in-memory caching system with LRU eviction policy in Python.
- Achieved sub-5ms lookup latency across 100,000 cached records.

Experience:
Software Engineering Intern | TechCorp (Summer 2025)
- Automated API regression testing suite using pytest, reducing release testing time by 30%.
- Refactored legacy database queries to improve indexing efficiency.
"""
        cursor.execute(
            """INSERT INTO resumes (user_id, filename, file_text, target_role)
               VALUES (?, ?, ?, ?)""",
            (user_id, "Alex_Mercer_Resume_2026.pdf", sample_resume_text, "Software Development Engineer (SDE)")
        )
        resume_id = cursor.lastrowid

        matched_kw = ["Python", "Java", "SQL", "FastAPI", "React", "Docker", "Git", "Data Structures", "Algorithms", "WebSockets"]
        missing_kw = ["Kubernetes", "Microservices", "CI/CD Pipeline", "System Design", "Unit Testing / TDD", "AWS / Cloud"]
        gaps = [
            "Lack of production cloud deployment experience (AWS/GCP)",
            "System design and high-level architectural trade-offs not prominently featured",
            "Distributed tracing and monitoring tools (Prometheus, Grafana) absent"
        ]
        suggs = [
            "Quantify business impact in project descriptions using the Google XYZ formula (Accomplished [X] as measured by [Y] by doing [Z]).",
            "Add a dedicated System Design project showcasing caching, load balancing, and rate limiting.",
            "Highlight CI/CD pipelines (GitHub Actions) to demonstrate automated deployment capabilities."
        ]

        cursor.execute(
            """INSERT INTO resume_analyses (resume_id, overall_score, structure_score, keyword_score, relevance_score, matched_keywords_json, missing_keywords_json, skill_gaps_json, suggestions_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (resume_id, 78.5, 84.0, 75.0, 76.5, json.dumps(matched_kw), json.dumps(missing_kw), json.dumps(gaps), json.dumps(suggs))
        )

        # 10. Initial Mock Interview Record
        cursor.execute(
            """INSERT INTO mock_interviews (user_id, interview_type, target_role, status, overall_score, feedback_summary, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "Technical", "Software Development Engineer", "Completed", 74.0, "Strong in basic data structures and OOP. Needs improvement in time complexity derivation for DP and deeper network protocol understanding.", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        mock_id = cursor.lastrowid

        q1 = "Explain how HashMap handles collisions in Java and what the time complexity becomes in the worst case."
        cursor.execute(
            """INSERT INTO interview_questions (mock_interview_id, question_text, category, expected_key_points, order_idx)
               VALUES (?, ?, ?, ?, ?)""",
            (mock_id, q1, "Technical - DSA & Java", "Chaining, linked list, treeification (Red-Black tree in Java 8+), O(log N) worst case", 1)
        )
        iq1_id = cursor.lastrowid

        r1 = "Java HashMap uses separate chaining. When two keys hash to the same bucket index, they are stored in a linked list. In Java 8, when the bucket size exceeds 8, it converts to a Red-Black tree so worst-case lookup becomes O(log n) instead of O(n)."
        cursor.execute(
            """INSERT INTO interview_responses (interview_question_id, user_response, technical_score, clarity_score, confidence_score, communication_score, relevance_score, feedback, key_strengths, improvement_areas)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (iq1_id, r1, 88.0, 85.0, 80.0, 85.0, 90.0, "Excellent explanation covering both separate chaining and Java 8 treeification.", "Accurate time complexities, mentioned Java 8 threshold of 8.", "Could mention threshold reduction back to linked list at count 6.")
        )

        # 11. Initial Progress Records (Simulating historical progress over past 7 days)
        for i in range(7, 0, -1):
            day_ts = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
            readiness = 58.0 + (7 - i) * 2.5
            cursor.execute(
                """INSERT INTO progress_records (user_id, readiness_score, dsa_score, dbms_score, os_score, cn_score, oop_score, aptitude_score, behavioral_score, coding_completion_pct, resume_score, interview_avg_score, study_plan_adherence, recorded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, readiness, 62.0 + (7-i), 72.0, 68.0, 48.0, 75.0, 70.0, 75.0, 45.0 + (7-i)*3, 78.5, 74.0, 70.0 + (7-i)*2, day_ts)
            )

        print("Database seeded successfully with realistic student preparation dataset!")

if __name__ == "__main__":
    seed()
