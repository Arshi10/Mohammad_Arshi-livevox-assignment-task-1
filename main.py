import Tests as Ts
import argparse

#Called by Main function
#It instantiate the class of Test.py
#which is having test cases

def main():
    parser = argparse.ArgumentParser(description="Need ASG Name")
    parser.add_argument('--asg_name', type=str, help='Asg Name', required=True)
    args = parser.parse_args()
    TE = Ts.Test_cases(asg_name=args.asg_name)
    TE.Test_A()
    TE.Test_B()


if __name__ == '__main__':
    main()


