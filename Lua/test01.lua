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
    local a = 1
    a = a + 2
end

