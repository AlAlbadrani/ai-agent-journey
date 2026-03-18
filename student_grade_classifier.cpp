/*


## 🧩 Challenge: **Student Grade Classifier**

### Problem:
Write a C++ program that:

1. Asks the user to enter **5 student scores** (0–100)
2. **Calculates the average** of the scores
3. **Classifies the average** using this grading scale:
   - **A** → 90–100
   - **B** → 80–89
   - **C** → 70–79
   - **D** → 60–69
   - **F** → Below 60
4. Prints the **average** and the **letter grade**

---

### 📌 Example Output:
```
Enter score 1: 85
Enter score 2: 90
Enter score 3: 78
Enter score 4: 92
Enter score 5: 70

Average: 83
Grade: B
```

---

### 💡 Things to think about:
- How will you **store** the scores?
- How will you **loop** through them?
- What's the cleanest way to handle the **grade classification**?

Take your time, think it through, and send me your solution either as **code text** or a **file path**. Good luck! 🚀

*/

#include <iostream>

int main(int argc, char const *argv[])
{
    std::string grade;
    int x;
    int average =0;
    std::cout << "Enter 5 scores between 0-100";
    for (int i = 0; i < 5; i++)
    {
        std::cin >> x;
        average += x;
    }
    
    average = average/5;
    if (average >= 90) {
        grade = "A";
    } else if (average >= 80) {
        grade = "B";
    } else if (average >= 70) {
        grade = "C";
    } else if (average >= 60) {
        grade = "D";
    } else {
        grade = "F";
    }

    std::cout << "Average: " << average << " Grade: " << grade << std::endl;
    return 0;
}
