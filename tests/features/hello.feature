Feature: Hello

  Scenario: Hello_world
    Given AWAIT 60 with delta 1
    Given assert global time
    Given END
    Given hello


  Scenario: Must_fail
    Given MUST FAIL
    Given AWAIT 10 with delta 1
    Given assert global time
    Given END
    Given END
    
  Scenario: ForChecking
    Given REPEAT 11
    Given MUST FAIL
    Given Value must be more then 10
    Given END
    Given Add 1
    Given END
    Given Value must be more then 10