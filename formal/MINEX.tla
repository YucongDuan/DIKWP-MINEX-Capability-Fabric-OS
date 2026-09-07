----------------------------- MODULE MINEX -----------------------------
EXTENDS Naturals, Sequences

CONSTANTS Draft, Planned, Leased, Executed, Verified, Settled, Stopped,
          Local, Peer, Market, Human

VARIABLES phase, authority, leaseValid, receiptValid, paymentExecuted, stopped

vars == <<phase, authority, leaseValid, receiptValid, paymentExecuted, stopped>>

Init == /\ phase = Draft
        /\ authority = 0
        /\ leaseValid = FALSE
        /\ receiptValid = FALSE
        /\ paymentExecuted = FALSE
        /\ stopped = FALSE

Plan == /\ phase = Draft /\ ~stopped
        /\ phase' = Planned
        /\ UNCHANGED <<authority, leaseValid, receiptValid, paymentExecuted, stopped>>

Lease == /\ phase = Planned /\ ~stopped
         /\ phase' = Leased
         /\ leaseValid' = TRUE
         /\ UNCHANGED <<authority, receiptValid, paymentExecuted, stopped>>

Execute == /\ phase \in {Planned, Leased} /\ ~stopped
           /\ (phase = Planned \/ leaseValid)
           /\ phase' = Executed
           /\ UNCHANGED <<authority, leaseValid, receiptValid, paymentExecuted, stopped>>

Verify == /\ phase = Executed /\ ~stopped
          /\ phase' = Verified
          /\ receiptValid' = TRUE
          /\ UNCHANGED <<authority, leaseValid, paymentExecuted, stopped>>

SettleProposal == /\ phase = Verified /\ receiptValid /\ ~stopped
                  /\ phase' = Settled
                  /\ paymentExecuted' = FALSE
                  /\ UNCHANGED <<authority, leaseValid, receiptValid, stopped>>

Stop == /\ ~stopped
        /\ stopped' = TRUE
        /\ phase' = Stopped
        /\ UNCHANGED <<authority, leaseValid, receiptValid, paymentExecuted>>

Next == Plan \/ Lease \/ Execute \/ Verify \/ SettleProposal \/ Stop

NoExternalAuthority == authority = 0
NoAutomaticPayment == paymentExecuted = FALSE
NoExecutionAfterStop == stopped => phase = Stopped
SettlementNeedsReceipt == phase = Settled => receiptValid

Spec == Init /\ [][Next]_vars
=============================================================================
