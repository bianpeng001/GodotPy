function hello()
    print("hello")
end

function add(a, b)
    return a + b
end

function test01()
    local op_meta = 
    {
        __add = function(a, b)
            print('add')
        end
    }
    op_meta.__index = op_meta

    local x = {}
    setmetatable(x, op_meta)
    local y = x + 1

end

function test02()
    -- LOADI 0 1
    local a = 1
    -- ADDI 0 0 3
    -- MMBINI 0 3 6 0
    a = a + 3

    -- LOADI 1 2 ; LOADI local(b) imm(2)
    local b = 2
    -- ADDI 1 0 3; ADDI output(b) input(a) imm(3)
    -- MMBINI 0 3 6 1; MMBINI input(a) imm(3) op(6) flip(1)
    b = 3 + a

end





