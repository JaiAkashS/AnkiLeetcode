import sys
from src.anki.add import add_problem
from src.anki.review import review_problems

def main():
    print("Welcome to the LeetCode Anki Tool!")
    while True:
        print("\nMenu:")
        print("1. Add a new problem")
        print("2. Review problems")
        print("3. Daily mode (review today's scheduled problems)")
        print("4. Bored mode (random problem by tag)")
        print("5. Statistics")
        print("6. Exit")
        choice = input("Choose an option (1-6): ")

        if choice == '1':
            add_problem()
            print("Problem added successfully!")

        elif choice == '2':
            print("Review Modes:")
            print("1. Recall entire solution")
            print("2. Partially blank out sections")
            review_choice = input("Choose a review mode (1-2): ")
            review_problems(review_choice)

        elif choice == '3':
            print("Daily Mode: Reviewing problems scheduled for today.")
            from src.anki.review import review_daily
            review_daily()

        elif choice == '4':
            print("Bored Mode: Reviewing a random problem by tag.")
            from src.anki.review import review_bored
            review_bored()

        elif choice == '5':
            print("Statistics:")
            from src.anki.review import print_statistics
            print_statistics()

        elif choice == '6':
            print("Exiting the application. Goodbye!")
            sys.exit()

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()