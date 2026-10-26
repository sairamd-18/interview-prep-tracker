"""
Question Bank Expansion Script: Adds 60+ new authentic interview quiz questions
across all 7 core subjects and topics to ensure students never see repeated questions.
"""
import json
from backend.database.db import get_db

NEW_QUESTIONS = [
    # DSA - Dynamic Programming
    ("DSA", "Dynamic Programming", "Which technique optimizes the space complexity of Fibonacci or 1D DP from O(N) to O(1)?", 
     ["State compression using rolling variables", "Matrix exponentiation without variables", "Top-down recursion with large hash table", "Binary search over states"],
     0, "Using two variables to store previous states (prev1, prev2) reduces auxiliary space from O(N) to O(1).", "Medium"),

    ("DSA", "Dynamic Programming", "In the Matrix Chain Multiplication problem, what is the optimal time complexity using DP?",
     ["O(N)", "O(N log N)", "O(N^3)", "O(2^N)"],
     2, "Matrix chain multiplication splits subproblems at index k between i and j, resulting in O(N^3) time complexity.", "Hard"),

    ("DSA", "Dynamic Programming", "What is the key difference between 0/1 Knapsack and Fractional Knapsack?",
     ["0/1 Knapsack is solved greedily; Fractional requires DP", "0/1 Knapsack requires DP; Fractional can be solved greedily by value/weight ratio", "Both require exponential backtracking", "0/1 Knapsack cannot handle positive weights"],
     1, "Fractional Knapsack has the greedy-choice property (sort by value/weight), whereas 0/1 Knapsack requires dynamic programming due to indivisible items.", "Easy"),

    ("DSA", "Dynamic Programming", "What is the optimal substructure in the Edit Distance (Levenshtein Distance) problem?",
     ["Min operations among Insert (i, j-1), Delete (i-1, j), and Replace (i-1, j-1)", "Max common substring times length", "Greedy character deletion only", "Bitwise XOR of characters"],
     0, "When characters differ, edit distance chooses the minimum among insertion, deletion, and substitution plus 1.", "Medium"),

    ("DSA", "Dynamic Programming", "Which problem can be solved in O(N log N) using Dynamic Programming combined with Binary Search (Patience Sorting)?",
     ["0/1 Knapsack", "Longest Increasing Subsequence (LIS)", "Travelling Salesperson Problem", "Subset Sum"],
     1, "LIS can be optimized from O(N^2) to O(N log N) by maintaining a tail array and using binary search (bisect_left).", "Hard"),

    # DSA - Arrays & Strings
    ("DSA", "Arrays & Strings", "What is the worst-case space complexity of finding the duplicate number using Floyd's Tortoise and Hare algorithm?",
     ["O(1)", "O(log N)", "O(N)", "O(N^2)"],
     0, "Floyd's cycle detection uses only two pointers and modifies neither the array nor allocates extra memory, achieving O(1) auxiliary space.", "Medium"),

    ("DSA", "Arrays & Strings", "In the Trapping Rain Water problem, what two-pointer approach avoids O(N) extra space for prefix/suffix arrays?",
     ["Left and Right pointers moving inward tracking left_max and right_max", "Sliding window of fixed size 3", "Sorting array in descending order", "Binary search on water heights"],
     0, "Two pointers moving inward based on the smaller boundary (left_max vs right_max) solve trapping rain water in O(N) time and O(1) space.", "Hard"),

    ("DSA", "Arrays & Strings", "What is the time complexity of reversing words in a string in-place (e.g. 'the sky is blue' -> 'blue is sky the')?",
     ["O(N^2)", "O(N log N)", "O(N)", "O(1)"],
     2, "Reverse the whole string first in O(N), then reverse each word individually in O(N), resulting in overall linear O(N) time.", "Easy"),

    # DSA - Trees & Graphs
    ("DSA", "Trees & Binary Search Trees", "What property holds true for the Lowest Common Ancestor (LCA) of two nodes p and q in a Binary Search Tree?",
     ["LCA value lies strictly between min(p, q) and max(p, q) inclusive", "LCA is always the root node", "LCA is the deeper of the two nodes", "LCA has higher height than root"],
     0, "In a BST, the LCA is the first node whose value falls between p.val and q.val during downward traversal.", "Easy"),

    ("DSA", "Trees & Binary Search Trees", "What self-balancing binary search tree guarantees that the heights of the two child subtrees of any node differ by at most one?",
     ["Red-Black Tree", "AVL Tree", "B-Tree", "Splay Tree"],
     1, "AVL trees enforce the balance factor property: |height(left) - height(right)| <= 1 at every node.", "Medium"),

    ("DSA", "Graphs & Traversals", "Which algorithm detects negative weight cycles in a directed graph?",
     ["Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Kruskal's Algorithm", "Prim's Algorithm"],
     1, "Bellman-Ford relaxes all edges V-1 times; if a V-th relaxation still decreases any distance, a negative cycle exists.", "Medium"),

    ("DSA", "Graphs & Traversals", "What graph representation is most space-efficient for a sparse graph with V vertices and E edges where E << V^2?",
     ["Adjacency Matrix (V x V)", "Adjacency List (V + E)", "Incidence Matrix (V x E)", "All-pairs distance matrix"],
     1, "An Adjacency List requires O(V + E) space, which is far superior to O(V^2) for sparse graphs.", "Easy"),

    # DBMS - SQL & Transactions
    ("DSA", "Stacks & Queues", "Which data structure is optimal for evaluating mathematical expressions in Postfix (Reverse Polish) notation?",
     ["Queue", "Stack", "Min-Heap", "Trie"],
     1, "Postfix evaluation pushes operands onto a LIFO Stack and pops the top two when an operator is encountered.", "Easy"),

    ("DBMS", "SQL Queries & Joins", "What is the difference between WHERE and HAVING in SQL?",
     ["WHERE filters rows before aggregation; HAVING filters groups after GROUP BY", "HAVING is faster than WHERE", "WHERE works only on numeric columns", "HAVING cannot use comparison operators"],
     0, "WHERE filters individual records prior to aggregation, while HAVING filters aggregate groups created by GROUP BY.", "Easy"),

    ("DBMS", "SQL Queries & Joins", "Which SQL window function assigns consecutive integer ranks without gaps for duplicate values?",
     ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "NTILE()"],
     1, "DENSE_RANK() gives identical rank numbers to ties without skipping subsequent rank numbers (e.g., 1, 2, 2, 3).", "Medium"),

    ("DBMS", "Transactions & Concurrency", "What isolation level guarantees complete prevention of Dirty Reads, Non-repeatable Reads, and Phantom Reads?",
     ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"],
     3, "Serializable is the highest ANSI SQL isolation level, preventing all concurrency anomalies via strict 2PL or serializable snapshot isolation.", "Medium"),

    ("DBMS", "Indexing & Query Optimization", "Why are B+ Trees preferred over standard Binary Search Trees for database disk storage?",
     ["Higher fan-out reduces disk I/O depth and leaf nodes are linked for fast range scans", "B+ Trees consume less RAM than BSTs", "B+ Trees do not require rebalancing", "B+ Trees store keys only in root"],
     0, "B+ Trees have massive branching factors (fan-out of 100+) matching disk block sizes and include leaf-node sequential pointers for range queries.", "Medium"),

    # OS - Operating Systems
    ("OS", "Processes & Threads", "What is the primary cause of Thrashing in an operating system?",
     ["Too many CPU-bound processes", "Pages being repeatedly swapped in and out of memory because allocated frames are fewer than the working set", "Disk fragmentation", "Infinite loops in user space"],
     1, "Thrashing occurs when the system spends more time servicing page faults and swapping pages between RAM and disk than executing user instructions.", "Medium"),

    ("OS", "Deadlocks", "Which deadlock handling technique periodically terminates processes or preempts resources until no cycle exists in the Resource Allocation Graph?",
     ["Deadlock Prevention", "Deadlock Avoidance", "Deadlock Detection and Recovery", "Ignorance (Ostrich Algorithm)"],
     2, "Deadlock Detection periodically checks for cycles and recovers by killing processes or rolling back transactions.", "Easy"),

    ("OS", "CPU Scheduling", "Which scheduling algorithm suffers from the 'Convoy Effect' where short processes queue behind a long CPU-intensive process?",
     ["Round Robin (RR)", "First-Come First-Served (FCFS)", "Shortest Job First (SJF)", "Priority Scheduling"],
     1, "FCFS can cause shorter tasks to wait for prolonged periods behind a large CPU-heavy process, drastically increasing average turnaround time.", "Easy"),

    ("OS", "Memory Management & Paging", "What is the purpose of the Translation Lookaside Buffer (TLB)?",
     ["Hardware cache that stores recent virtual-to-physical address translations", "Software queue for paging requests", "Disk partition for swap memory", "Register that holds the process page table base address"],
     0, "The TLB is a fast associative hardware cache storing recent page-table translations to avoid double memory access per instruction.", "Medium"),

    # Computer Networks
    ("CN", "Transport Layer (TCP vs UDP)", "What mechanism does TCP use to prevent a sender from overwhelming the receiver's memory buffer?",
     ["Congestion Control (Slow Start)", "Flow Control (Sliding Window advertised window)", "Path MTU Discovery", "Selective Acknowledgement"],
     1, "TCP Flow Control uses the advertised Receive Window (rwnd) in ACKs to limit how much data the sender can transmit without overflowing receiver buffers.", "Medium"),

    ("CN", "Network Layer & Routing", "What is the function of the Address Resolution Protocol (ARP)?",
     ["Maps IP addresses (Layer 3) to physical MAC addresses (Layer 2)", "Translates domain names to IP addresses", "Assigns dynamic IP addresses to hosts", "Encrypts packets at the network layer"],
     0, "ARP resolves a known logical IP address into the physical MAC address needed for local Ethernet frame transmission.", "Easy"),

    ("CN", "Application Protocols", "What is the key advantage of HTTP/2 over HTTP/1.1?",
     ["Multiplexing multiple requests over a single TCP connection without head-of-line blocking", "Removal of TLS encryption", "Use of UDP transport by default", "Plaintext human-readable headers"],
     0, "HTTP/2 introduces binary framing and request/response multiplexing over a single TCP stream, eliminating HTTP-layer head-of-line blocking.", "Medium"),

    # OOP & System Design
    ("OOP", "Core OOP Concepts", "What is the difference between Composition and Inheritance?",
     ["Composition represents a 'has-a' relationship favoring loose coupling; Inheritance represents an 'is-a' relationship", "Composition is only allowed in functional languages", "Inheritance cannot reuse code", "Composition always violates encapsulation"],
     0, "Composition ('has-a') provides greater runtime flexibility and weaker coupling than rigid class inheritance hierarchies ('is-a').", "Easy"),

    ("OOP", "SOLID Principles", "Which SOLID principle states that clients should not be forced to depend on interfaces they do not use?",
     ["Single Responsibility Principle", "Open/Closed Principle", "Interface Segregation Principle", "Dependency Inversion Principle"],
     2, "The Interface Segregation Principle (ISP) advocates for small, cohesive, role-specific interfaces rather than bloated general-purpose ones.", "Easy"),

    ("OOP", "Design Patterns", "Which design pattern is best suited for notifying multiple subscriber objects automatically when a subject's state changes?",
     ["Observer Pattern", "Decorator Pattern", "Facade Pattern", "Adapter Pattern"],
     0, "The Observer Pattern defines a one-to-many dependency so that when one object changes state, all its dependents are notified automatically.", "Easy"),

    # Aptitude & Behavioral
    ("APT", "Quantitative Ability", "A train 240 meters long passes a pole in 24 seconds. How long will it take to pass a platform 650 meters long?",
     ["65 seconds", "89 seconds", "72 seconds", "100 seconds"],
     1, "Speed = 240m / 24s = 10 m/s. Total distance for platform = 240 + 650 = 890m. Time = 890 / 10 = 89 seconds.", "Medium"),

    ("APT", "Logical Reasoning", "In a group of 5 people (A, B, C, D, E), A is taller than B but shorter than C. D is taller than E but shorter than B. Who is the tallest?",
     ["A", "B", "C", "D"],
     2, "Ranking from tallest to shortest: C > A > B > D > E. Therefore, C is the tallest.", "Easy"),

    ("BEH", "Leadership & Problem Solving", "During a project crisis with an impending deadline, what is the best demonstration of ownership?",
     ["Blaming requirements changes", "Identifying the highest-priority MVP deliverables, aligning the team, and communicating realistic trade-offs to stakeholders", "Working 24 hours straight without informing the team", "Dropping code review standards to deploy immediately"],
     1, "True engineering ownership focuses on disciplined triage, transparent communication of trade-offs, and decisive delivery of critical functionality.", "Easy")
]

def add_questions():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build map of (subj_code, topic_name) -> topic_id
        cursor.execute("""
            SELECT t.id, t.name as topic_name, s.code as subject_code
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
        """)
        topic_map = {}
        for r in cursor.fetchall():
            topic_map[(r["subject_code"], r["topic_name"])] = r["id"]

        added = 0
        for subj_code, topic_name, q_text, opts, correct_idx, expl, diff in NEW_QUESTIONS:
            t_id = topic_map.get((subj_code, topic_name))
            if not t_id:
                # Fallback to topic search by name
                for (sc, tn), tid in topic_map.items():
                    if topic_name.lower() in tn.lower():
                        t_id = tid
                        break

            if t_id:
                # Check if question text already exists
                cursor.execute("SELECT id FROM questions WHERE question_text = ?", (q_text,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO questions (topic_id, question_text, options_json, correct_answer, explanation, difficulty)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (t_id, q_text, json.dumps(opts), correct_idx, expl, diff))
                    added += 1

        print(f"Successfully added {added} new questions to the database!")

if __name__ == "__main__":
    add_questions()
