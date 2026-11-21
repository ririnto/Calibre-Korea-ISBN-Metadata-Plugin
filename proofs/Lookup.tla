------------------------------- MODULE Lookup -------------------------------
EXTENDS Naturals

VARIABLES phase, isbnPresent, requests

Init == /\ phase = "start"
        /\ isbnPresent \in BOOLEAN
        /\ requests = 0

BuildRequest == /\ phase = "start"
                /\ isbnPresent
                /\ phase' = "ready"
                /\ UNCHANGED <<isbnPresent, requests>>

StopBeforeRequest == /\ phase = "start"
                     /\ phase' = "done"
                     /\ UNCHANGED <<isbnPresent, requests>>

Request == /\ phase = "ready"
           /\ phase' = "done"
           /\ requests' = requests + 1
           /\ UNCHANGED isbnPresent

Finish == /\ phase = "done"
          /\ UNCHANGED <<phase, isbnPresent, requests>>

Next == BuildRequest \/ StopBeforeRequest \/ Request \/ Finish
Spec == Init /\ [][Next]_<<phase, isbnPresent, requests>>

MissingISBNStopsRequest == ~isbnPresent => requests = 0
AtMostOneRequest == requests <= 1
=============================================================================
