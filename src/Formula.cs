using System;
using System.Collections.Generic;
using System.Text;

namespace Rona
{
    //
    // bianpeng001@163.com
    // 一个表达式计算的工具，用来做公式，甚至稍微弱一点的脚本
    // 优点:
    // 小巧，单个文件
    // 在C#端实现，不用嵌入虚拟机
    // 不用跨语言调用和数据传输
    // 不是解释执行，会快不少
    // 不是字节码，功能还到不了那个程度
    // 支持多线程
    //
    // 用途，数值中的运算，打算跟可视化配置blockly结合用
    //
    // see: https://github.com/google/blockly
    //      https://developers.google.com/blockly
    //
    //
    public static class Formula
    {
        //
        // builtin function type
        //
        public delegate Value BuiltinFunc(Env env, IExpression[] arguments);

        //
        // 数据类型
        //
        public enum DataType
        {
            None,
            Void,
            Nil, // Null 是一个特殊类型

            Bool,
            Int32,
            Int64,
            Double,
            String,

            Expression,
            BuiltinFunc,
        }

        //
        // 数值的容器
        //
        public struct Value
        {
            public static readonly Value Nil = new Value() { type = DataType.Nil };

            public DataType type;
            public long value;
            public object obj;

            public bool GetBool() => value != 0;
            public int GetInt32() => (int)value;
            public long GetInt64() => value;

            public float GetSingle()
            {
                unsafe
                {
                    fixed (long* ptr = &value)
                    {
                        return *(float*)ptr;
                    }
                }
            }

            public double GetDouble()
            {
                unsafe
                {
                    fixed (long* ptr = &value)
                    {
                        return *(double*)ptr;
                    }
                }
            }

            public string GetString() => (string)obj;
            public IExpression GetExpression() => (IExpression)obj;
            public BuiltinFunc GetFunc() => (BuiltinFunc)obj;

            public string GetRepr()
            {
                switch(type)
                {
                    case DataType.None:
                        return "none";
                    case DataType.Void:
                        return "void";
                    case DataType.Nil:
                        return "nil";
                    case DataType.Bool:
                        return GetBool() ? "true" : "false";

                    case DataType.Int32:
                    case DataType.Int64:
                        return GetInt64().ToString();
                    case DataType.Double:
                        return GetDouble().ToString();
                    case DataType.String:
                        return GetString();
                    
                    case DataType.BuiltinFunc:
                    case DataType.Expression:
                        if (obj != null)
                            return obj.ToString();
                        else
                            return "null";
                    default:
                        return ToString();
                }
            }

            public override string ToString()
            {
                return $"({type},{value},{obj})";
            }

            private static long Convert(double value)
            {
                unsafe
                {
                    double* ptr = &value;
                    return *(long*)ptr;
                }
            }

            public static implicit operator Value(bool value) => 
                new Value() { type = DataType.Bool, value = value ? -1 : 0 };
            public static implicit operator Value(int value) => 
                new Value() { type = DataType.Int32, value = value };
            public static implicit operator Value(long value) => 
                new Value() { type = DataType.Int64, value = value };
            public static implicit operator Value(double value) => 
                new Value() { type = DataType.Double, value = Convert(value) };
            public static implicit operator Value(string value) => 
                new Value() { type = DataType.String, obj = value };
            public static implicit operator Value(BuiltinFunc value) => 
                new Value() { type = DataType.BuiltinFunc, obj = value };
        }

        //
        // 全局变量
        //
        public class Env
        {
            private readonly Dictionary<string, IExpression> _G = new Dictionary<string, IExpression>();

            public Env()
            {
                _G["print"] = new ConstExpr(new BuiltinFunc(Print));
            }

            public IExpression this[string name]
            {
                get => _G[name];
                set => _G[name] = value;
            }
        }


        // 核心实现，一个表达式
        public interface IExpression
        {
            Value Eval(Env env);
        }

        // 二目运算符
        public class Op2Expr : IExpression
        {
            public int level;
            // support two operands
            public  IExpression oprand1;
            public IExpression oprand2;
            public Func<Env, IExpression, IExpression, Value> func;

            public Value Eval(Env env) => func(env, oprand1, oprand2);
        }

        // 常量表达式
        public class ConstExpr : IExpression
        {
            private Value value;

            public ConstExpr(in Value value)
            {
                this.value = value;
            }

            public Value Eval(Env env)
            {
                return value;
            }
        }

        // 函数调用
        public class CallExpr : IExpression
        {
            private IExpression[] arguments;

            private IExpression func;

            public CallExpr(IExpression func, IExpression[] arguments)
            {
                this.func = func;
                this.arguments = arguments;
            }

            public Value Eval(Env env)
            {
                var f = func.Eval(env);
                return f.type switch
                {
                    DataType.BuiltinFunc => f.GetFunc().Invoke(env, arguments),
                    _ => throw new InvalidOperationException(),
                };
            }
        }

        // 变量访问, 这个需要缓存一下，挺多的实际上
        public class IdentityExpr : IExpression
        {
            public readonly string name;

            public IdentityExpr(string name)
            {
                this.name = name;
            }

            public Value Eval(Env env)
            {
                return env[name].Eval(env);
            }
        }

        // 多个表达式，比如前面想输出点东西看看
        public class StmtsExpr : IExpression
        {
            public IExpression[] stmts;

            public Value Eval(Env env)
            {
                Value value = new Value() { type = DataType.Nil };
                for(int i = 0; i < stmts.Length; ++i)
                {
                    value = stmts[i].Eval(env);
                }
                return value;
            }
        }

        public class IndexExpr : IExpression
        {
            public IExpression main;
            public IExpression index;

            public Value Eval(Env env)
            {
                return new Value();
            }
        }

        //----------------------------------------------------------------------------
        // parser and tokenizer
        //----------------------------------------------------------------------------

        public class FormulaException : Exception
        {

        }

        private static IExpression ParseAtom(Tokenizer tokenizer)
        {
            ref var token = ref tokenizer.token;

            if (token.type == TokenType.INT)
            {
                var value = ParseInteger(tokenizer.input, token.start, token.end, 10);
                tokenizer.Eat(TokenType.INT);
                return new ConstExpr(value);
            }
            else if (token.type == TokenType.NUM)
            {
                var value = ParseNumber(tokenizer.input, token.start, token.end);
                tokenizer.Eat(TokenType.NUM);
                return new ConstExpr(value);
            }
            else if (token.type == TokenType.STR)
            {
                var value = tokenizer.input.Substring(token.start + 1, token.end - token.start - 2);
                tokenizer.Eat(TokenType.STR);
                return new ConstExpr(value);
            }
            else if (token.type == TokenType.ID)
            {
                // 识别成ID, 只能是变量，变量的查找顺序，LGB
                var identity = tokenizer.input.Substring(token.start, token.end - token.start);
                tokenizer.Eat(TokenType.ID);

                if (tokenizer.token.type == TokenType.LP)
                {
                    var call = new CallExpr(GetCached(identity),
                        ParseArguments(tokenizer));
                    
                    return call;
                }
            }
            else if (token.type == TokenType.LP)
            {
                tokenizer.Eat(TokenType.LP);
                var expr = ParseExpr(tokenizer);
                if (token.type != TokenType.RP)
                    throw new FormulaException();
                tokenizer.Eat(TokenType.RP);
                return expr;
            }

            throw new FormulaException();
        }

        private static double ParseNumber(string input, int start, int end)
        {
            int left = 0;

            int i = start;
            for(; i < end; ++i)
            {
                char c = input[i];
                if (IsDigit(c))
                    left += 10 * left + (c - '0');
                else if (c == '.')
                    break;
                else
                    throw new FormulaException();
            }

            ++i;
            double right = 0;
            double baseNum = 1.0;
            for (; i < end; ++i)
            {
                char c = input[i];
                if (IsDigit(c))
                {
                    baseNum *= 0.1;
                    right += baseNum * (c - '0');
                }
                else
                    throw new FormulaException();
            }

            return left + right;
        }

        private static readonly Dictionary<string, IdentityExpr> identityCache = new Dictionary<string, IdentityExpr>();
        private static IdentityExpr GetCached(string identity)
        {
            if (identityCache.TryGetValue(identity, out var result))
                return result;
            result = new IdentityExpr(identity);
            identityCache.Add(identity, result);
            return result;
        }

        private static IExpression[] ParseArguments(Tokenizer tokenizer)
        {
            tokenizer.Eat(TokenType.LP);
            List<IExpression> aList = new List<IExpression>();
            while (true)
            {
                var item = ParseExpr(tokenizer);
                aList.Add(item);
                if (tokenizer.token.type == TokenType.COMMA)
                    tokenizer.Eat(TokenType.COMMA);
                else if (tokenizer.token.type == TokenType.RP)
                {
                    tokenizer.Eat(TokenType.RP);
                    break;
                }
                else
                    throw new FormulaException();
            }
            
            return aList.ToArray();
        }

        private static int ParseInteger(string input, int start, int end, int baseNumber)
        {
            int value = 0;
            for(int i = start; i < end; ++i)
            {
                var c = input[i];
                value = value * baseNumber + (c - '0');
            }
            return value;
        }

        private static IExpression ParseExpr(Tokenizer tokenizer)
        {
            IExpression expr = ParseAtom(tokenizer);
            for (; ; )
            {
                ref var token = ref tokenizer.token;

                if (token.IsEof ||
                        token.type == TokenType.SEMI ||
                        token.type ==  TokenType.COMMA ||
                        token.type == TokenType.RP)
                    break;
                else if (token.type == TokenType.OP)
                {
                    var c = tokenizer.input[token.start];

                    tokenizer.Eat(TokenType.OP);
                    var operand2 = ParseAtom(tokenizer);

                    var op = new Op2Expr()
                    {
                        oprand1 = expr,
                        oprand2 = operand2,
                    };
                    op.func = c switch
                    {
                        '+' => Op_Add,
                        '-' => Op_Sub,
                        '*' => Op_Mul,
                        '/' => Op_Div,
                        '%' => Op_Mod,
                        _ => throw new FormulaException(),
                    };

                    // 这里要处理优先级
                    if (c == '*' || c == '/')
                        op.level = 1;
                    else
                        op.level = 0;
                    if (expr is Op2Expr op1 && op.level > op1.level)
                    {
                        op.oprand1 = op1.oprand2;
                        op1.oprand2 = op;
                        expr = op1;
                    }
                    else
                    {
                        expr = op;
                    }
                }
                else
                {
                    throw new FormulaException();
                }
            }
            return expr;
        }

        private static bool IsLetter(char c)
        {
            return c == '_' ||
                (c >= 'a' && c <= 'z') ||
                (c >= 'A' && c <= 'Z');
        }

        private static bool IsOp(char c)
        {
            return c == '+' ||
                c == '-' ||
                c == '*' ||
                c == '/' ||
                c == '%';
        }

        private static bool IsDigit(char c)
        {
            return c >= '0' && c <= '9';
        }

        private static void SkipSpace(string input, ref int i)
        {
            for(; i < input.Length; ++i)
            {
                var c = input[i];
                if (c != ' ' && c != '\t' && c != '\n')
                    break;
            }
        }

        public static IExpression Parse(string input)
        {
            var tokenizer = new Tokenizer(input);
            tokenizer.Eat(TokenType.NONE);
            var expr = ParseExpr(tokenizer);
            if (tokenizer.token.IsEof)
                return expr;

            var aList = new List<IExpression>();
            aList.Add(expr);
            while (tokenizer.token.type == TokenType.SEMI)
            {
                tokenizer.Eat(TokenType.SEMI);
                aList.Add(ParseExpr(tokenizer));
            }
            return new StmtsExpr() { stmts = aList.ToArray() };
        }

        //
        //
        //
        private enum TokenType
        {
            NONE,

            INT,
            NUM,
            STR,
            ID,
            
            OP, // +-*/%
            
            LP, // (
            RP, // )
            LBracket, // [
            RBracket, // [
            LBrace, // {
            RBrace, // }
            ASSIGN, // =
            
            COMMA, // ,
            COLON, // :
            SEMI, // ;

            EQ, // ==
            NEQ, // !=
            LT, // <
            LE, // <=
            GT, // >
            GE, // >=

            // keyword
            FUN, // function f(a,b,c,d) end
            
            IF,
            THEN,
            ELSE,

            FOR,
            WHILE,
            DO,
            END,

            AND,
            OR,
            XOR,

            LOCAL,
            RETURN,
            BREAK,
            GOTO,
            CLASS,

            EOF,
        }

        private struct Token
        {
            public TokenType type;
            // 单个字符的时候，这个code有用
            public int charcode;
            // end is excluded
            public int start, end;

            public bool IsEof => type == TokenType.EOF;
        }

        private class Tokenizer
        {
            public readonly string input;
            private int index;

            public Tokenizer(string formula)
            {
                this.input = formula;
                this.index = 0;
            }

            public Token token;

            public void Eat(TokenType type)
            {
                if (token.type != type)
                    throw new FormulaException();

                token = ParseToken();
            }

            private Token ParseToken()
            {
                SkipSpace(input, ref index);

                if (index >= input.Length)
                {
                    return new Token() { type = TokenType.EOF };
                }

                var c = this.input[index];
                if (IsDigit(c))
                {
                    var start = index;
                    ++index;
                    for (; index < input.Length; ++index)
                    {
                        var c1 = this.input[index];
                        if (!IsDigit(c1))
                            break;
                    }
                    if (index < input.Length && this.input[index] == '.')
                    {
                        ++index;
                        for (; index < input.Length; ++index)
                        {
                            var c1 = this.input[index];
                            if (!IsDigit(c1))
                                break;
                        }
                        return new Token() { type = TokenType.NUM, start = start, end = index };
                    }
                    else
                    {
                        return new Token() { type = TokenType.INT, start = start, end = index };
                    }

                    // TODO: 支持多个格式，浮点的多个格式
                }
                else if (IsLetter(c) || c == '_')
                {
                    var start = index;
                    ++index;
                    for (; index < input.Length; ++index)
                    {
                        var c1 = this.input[index];
                        if (!IsLetter(c1) && !IsDigit(c1) && c != '_')
                            break;
                    }
                    return new Token() { type = TokenType.ID, start = start, end = index };
                }
                else if (c == '\'' || c == '"')
                {
                    var start = index;
                    ++index;
                    for(; index < input.Length; ++index)
                    {
                        var c1 = this.input[index];
                        if (c1 == c)
                        {
                            ++index;
                            break;
                        }
                    }
                    return new Token() { type = TokenType.STR, start = start, end = index };
                }
                else if (IsOp(c))
                {
                    return new Token()
                    {
                        type = TokenType.OP,
                        charcode = c,
                        start = index++
                    };
                }

                // 匹配单字符的控制字符
                TokenType type = c switch
                {
                    '(' => TokenType.LP,
                    ')' => TokenType.RP,
                    ',' => TokenType.COMMA,
                    ';' => TokenType.SEMI,
                    _ => TokenType.NONE,
                };
                if (type != TokenType.NONE)
                {
                    return new Token()
                    {
                        type = type,
                        charcode = c,
                        start = index++,
                    };
                }

                throw new FormulaException();
            }
        }

        //----------------------------------------------------------------------------
        // runtime
        //----------------------------------------------------------------------------

        // 内部的对象
        private class FObject
        {
            // 内部的存储格式，也是两种，这样比较高效
            private Dictionary<string, Value> dict;
            private Value[] array;

            public Value GetItem(in Value index)
            {
                return Value.Nil;
            }

            public void SetItem(in Value index, in Value value)
            {
                if (index.type == DataType.Int64 || index.type == DataType.Int32)
                {

                }
                else if (index.type == DataType.String)
                {

                }
                else
                {
                    throw new FormulaException();
                }
            }
        }

        #region 数值运算类型转换

        private abstract class Op2TypeMap
        {
            public Value Eval(in Value left, in Value right)
            {
                switch(left.type)
                {
                    case DataType.Int32:
                        return right.type switch
                        {
                            DataType.Int32 => (Value)DoEval(left.GetInt32(), right.GetInt32()),
                            DataType.Int64 => (Value)DoEval(left.GetInt32(), right.GetInt64()),
                            DataType.Double => (Value)DoEval(left.GetInt32(), right.GetDouble()),
                            DataType.String => (Value)DoEval(left.GetInt32(), right.GetString()),
                            _ => throw new FormulaException(),
                        };

                    case DataType.Int64:
                        return right.type switch
                        {
                            DataType.Int32 => (Value)DoEval(left.GetInt64(), right.GetInt32()),
                            DataType.Int64 => (Value)DoEval(left.GetInt64(), right.GetInt64()),
                            DataType.Double => (Value)DoEval(left.GetInt64(), right.GetDouble()),
                            DataType.String => (Value)DoEval(left.GetInt64(), right.GetString()),
                            _ => throw new FormulaException(),
                        };

                    case DataType.Double:
                        return right.type switch
                        {
                            DataType.Int32 => (Value)DoEval(left.GetDouble(), right.GetInt32()),
                            DataType.Int64 => (Value)DoEval(left.GetDouble(), right.GetInt64()),
                            DataType.Double => (Value)DoEval(left.GetDouble(), right.GetDouble()),
                            DataType.String => (Value)DoEval(left.GetDouble(), right.GetString()),
                            _ => throw new FormulaException(),
                        };

                    case DataType.String:
                        return right.type switch
                        {
                            DataType.Int32 => (Value)DoEval(left.GetString(), right.GetInt32()),
                            DataType.Int64 => (Value)DoEval(left.GetString(), right.GetInt64()),
                            DataType.Double => (Value)DoEval(left.GetString(), right.GetDouble()),
                            DataType.String => (Value)DoEval(left.GetString(), right.GetString()),
                            _ => throw new FormulaException(),
                        };
                }

                throw new FormulaException();
            }

            protected virtual int DoEval(int left, int right)
            {
                throw new FormulaException();
            }
            protected virtual long DoEval(int left, long right)
            {
                throw new FormulaException();
            }
            protected virtual double DoEval(int left, double right)
            {
                throw new FormulaException();
            }
            protected virtual string DoEval(int left, string right)
            {
                throw new FormulaException();
            }


            protected virtual long DoEval(long left, int right)
            {
                throw new FormulaException();
            }
            protected virtual long DoEval(long left, long right)
            {
                throw new FormulaException();
            }
            protected virtual double DoEval(long left, double right)
            {
                throw new FormulaException();
            }
            protected virtual string DoEval(long left, string right)
            {
                throw new FormulaException();
            }

            protected virtual double DoEval(double left, int right)
            {
                throw new FormulaException();
            }
            protected virtual double DoEval(double left, long right)
            {
                throw new FormulaException();
            }
            protected virtual double DoEval(double left, double right)
            {
                throw new FormulaException();
            }
            protected virtual string DoEval(double left, string right)
            {
                throw new FormulaException();
            }

            protected virtual string DoEval(string left, int right)
            {
                throw new FormulaException();
            }
            protected virtual string DoEval(string left, long right)
            {
                throw new FormulaException();
            }
            protected virtual string DoEval(string left, double right)
            {
                throw new FormulaException();
            }
            protected virtual string DoEval(string left, string right)
            {
                throw new FormulaException();
            }
        }

        private class Op2TypeMap_Add : Op2TypeMap
        {
            protected override int DoEval(int left, int right)
            {
                return left + right;
            }

            protected override long DoEval(int left, long right)
            {
                return left + right;
            }

            protected override double DoEval(int left, double right)
            {
                return left + right;
            }

            protected override string DoEval(int left, string right)
            {
                return left + right;
            }

            protected override long DoEval(long left, int right)
            {
                return left + right;
            }

            protected override long DoEval(long left, long right)
            {
                return left + right;
            }

            protected override double DoEval(long left, double right)
            {
                return left + right;
            }

            protected override string DoEval(long left, string right)
            {
                return left + right;
            }

            protected override double DoEval(double left, int right)
            {
                return left + right;
            }

            protected override double DoEval(double left, long right)
            {
                return left + right;
            }

            protected override double DoEval(double left, double right)
            {
                return left + right;
            }

            protected override string DoEval(double left, string right)
            {
                return left + right;
            }

            protected override string DoEval(string left, int right)
            {
                return left + right;
            }

            protected override string DoEval(string left, long right)
            {
                return left + right;
            }

            protected override string DoEval(string left, double right)
            {
                return left + right;
            }

            protected override string DoEval(string left, string right)
            {
                return left + right;
            }
        }

        private class Op2TypeMap_Sub : Op2TypeMap
        {
            protected override int DoEval(int left, int right)
            {
                return left - right;
            }

            protected override long DoEval(int left, long right)
            {
                return left - right;
            }

            protected override double DoEval(int left, double right)
            {
                return left - right;
            }

            protected override long DoEval(long left, int right)
            {
                return left - right;
            }

            protected override long DoEval(long left, long right)
            {
                return left - right;
            }

            protected override double DoEval(long left, double right)
            {
                return left - right;
            }

            protected override double DoEval(double left, int right)
            {
                return left - right;
            }

            protected override double DoEval(double left, long right)
            {
                return left - right;
            }

            protected override double DoEval(double left, double right)
            {
                return left - right;
            }
        }

        private class Op2TypeMap_Mul : Op2TypeMap
        {
            protected override int DoEval(int left, int right)
            {
                return left * right;
            }

            protected override long DoEval(int left, long right)
            {
                return left * right;
            }

            protected override double DoEval(int left, double right)
            {
                return left * right;
            }

            protected override long DoEval(long left, int right)
            {
                return left * right;
            }

            protected override long DoEval(long left, long right)
            {
                return left * right;
            }

            protected override double DoEval(long left, double right)
            {
                return left * right;
            }

            protected override double DoEval(double left, int right)
            {
                return left * right;
            }

            protected override double DoEval(double left, long right)
            {
                return left * right;
            }

            protected override double DoEval(double left, double right)
            {
                return left * right;
            }

            protected override string DoEval(string left, int right)
            {
                var sb = new StringBuilder();
                for(int i = 0; i < right; ++i)
                    sb.Append(left);
                return sb.ToString();
            }
        }

        private class Op2TypeMap_Div : Op2TypeMap
        {
            protected override int DoEval(int left, int right)
            {
                return left / right;
            }

            protected override long DoEval(int left, long right)
            {
                return left / right;
            }

            protected override double DoEval(int left, double right)
            {
                return left / right;
            }

            protected override long DoEval(long left, int right)
            {
                return left / right;
            }

            protected override long DoEval(long left, long right)
            {
                return left / right;
            }

            protected override double DoEval(long left, double right)
            {
                return left / right;
            }

            protected override double DoEval(double left, int right)
            {
                return left / right;
            }

            protected override double DoEval(double left, long right)
            {
                return left / right;
            }

            protected override double DoEval(double left, double right)
            {
                return left / right;
            }
        }

        private static Op2TypeMap add = new Op2TypeMap_Add();
        private static Op2TypeMap sub = new Op2TypeMap_Sub();
        private static Op2TypeMap mul = new Op2TypeMap_Mul();
        private static Op2TypeMap div = new Op2TypeMap_Div();

        #endregion

        private static Value Op_Add(Env env, IExpression left, IExpression right)
        {
            var a = left.Eval(env);
            var b = right.Eval(env);

            return add.Eval(a, b);
        }

        private static Value Op_Sub(Env env, IExpression left, IExpression right)
        {
            var a = left.Eval(env);
            var b = right.Eval(env);
            return sub.Eval(a, b);
        }

        private static Value Op_Mul(Env env, IExpression left, IExpression right)
        {
            var a = left.Eval(env);
            var b = right.Eval(env);
            return mul.Eval(a, b);
        }

        private static Value Op_Div(Env env, IExpression left, IExpression right)
        {
            var a = left.Eval(env);
            var b = right.Eval(env);
            return div.Eval(a, b);
        }

        private static Value Op_Mod(Env env, IExpression left, IExpression right)
        {
            var a = left.Eval(env);
            var b = right.Eval(env);
            return a.GetInt32() % b.GetInt32();
        }

        private static Value Print(Env env, IExpression[] arguments)
        {
            for(int i = 0; i < arguments.Length; i++)
            {
                if (i > 0)
                    Console.Write(' ');

                var value = arguments[i].Eval(env);
                Console.Write(value.GetRepr());
            }
            Console.WriteLine();

            return new Value() { type = DataType.Void };
        }

        //----------------------------------------------------------------------------
        // tests
        //----------------------------------------------------------------------------
        public static void Test()
        {
            var env = new Env();

            var test1 = Parse("123 + 456 - 111");
            Console.WriteLine(test1.Eval(env));

            var test2 = Parse("1 + 2 + 3 + 4 +5+6+7+8+9+10");
            Console.WriteLine(test2.Eval(env));

            var test3 = Parse("print('hello', 1234)");
            Console.WriteLine(test3.Eval(env));

            var test4 = Parse("print('hello');print('world');1245");
            Console.WriteLine(test4.Eval(env));

            var test5 = Parse("1 + 1.234");
            Console.WriteLine(test5.Eval(env));

            var test6 = Parse("'x'*10");
            Console.WriteLine(test6.Eval(env));

            var test7 = Parse("print('x'*10 + 'abcd')");
            Console.WriteLine(test7.Eval(env));

            var test8 = Parse("1 + 2 * 3");
            Console.WriteLine(test8.Eval(env));

            var test9 = Parse("(1 + 2) * 3");
            Console.WriteLine(test9.Eval(env));
        }
    }

}



