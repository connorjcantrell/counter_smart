from pyteal import *


def approval_program():

    on_create = Seq(
        [
            App.globalPut(Bytes("Count"), Int(0)),
            Return(Int(1))
        ]
    )

    on_opt_in = Return(Int(0))
    on_close_out = Return(Int(0))
    on_update = Return(Int(0))
    on_delete = Return(Int(0))
    
    # Scratch space/ Temporary storage
    scratch_count = ScratchVar(TealType.uint64)

    add = Seq([
        # Current value of global variable Count is read and placed in scratch space
        scratch_count.store(App.globalGet(Bytes("Count"))),
        App.globalPut(Bytes("Count"), scratch_count.load() + Int(1)),
        Return(Int(1))
    ])
    
    deduct = Seq([
        scratch_count.store(App.globalGet(Bytes("Count"))),
        If(scratch_count.load() > Int(0),
            App.globalPut(Bytes("Count"), scratch_count.load() - Int(1)),
        ),
        Return(Int(1))
    ])

    on_noop = Cond(
        [And(
            # Get the number of transactions in this atomic transaction group
            Global.group_size() == Int(1),
            Txn.application_args[0] == Bytes("Add")
        ), add],
        [And(
            Global.group_size() == Int(1),
            Txn.application_args[0] == Bytes("Deduct")
        ), deduct],
    )




    # Cond expression behaves like a switch statement, first to return true
    # This can be thought of as our router
    program = Cond(
            [Txn.application_id() == Int(0), on_create],
            [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
            [Txn.on_completion() == OnComplete.CloseOut, on_close_out],
            [Txn.on_completion() == OnComplete.UpdateApplication, on_update],
            [Txn.on_completion() == OnComplete.DeleteApplication, on_delete],
            [Txn.on_completion() == OnComplete.NoOp, on_noop]
    )
    return Int(1)


def clear_state_program():
    return Int(1)

if __name__ == "__main__":
    with open("simplestorage_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("simplestorage_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)
