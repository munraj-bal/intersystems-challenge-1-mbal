Class dc.challenge.Solution Extends %RegisteredObject
{

/// Run the Gaia flux variability analysis by importing and executing
/// the standalone solution.py module.
ClassMethod Run() [ Language = python ]
{
    import sys
    sys.path.insert(0, "/home/irisowner/dev")
    import solution
    solution.main()
}

}