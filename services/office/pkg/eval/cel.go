package eval

import (
	"github.com/HackerDom/ructfe2020/pkg/eval/funcs"
	"github.com/google/cel-go/cel"
)

func Eval(expr string, inerCtx map[string]string) (bool, error) {
	vars := make(map[string]interface{}, 5)
	e, opts, err := createEnv(inerCtx, vars)
	if err != nil {
		return false, err
	}
	ast, iss := e.Compile(expr)
	if iss.Err() != nil {
		return false, iss.Err()
	}
	prg, err := e.Program(ast, opts...)
	if err != nil {
		return false, err
	}
	out, _, err := prg.Eval(map[string]interface{}{})
	if err != nil {
		return false, err
	}
	return out.Value().(bool), nil
}

func createEnv(inerCtx map[string]string, vars map[string]interface{}) (*cel.Env, []cel.ProgramOption, error) {
	opts, fs := funcs.EnvOptions(inerCtx)
	opts = append(opts, funcs.VarsDecls(vars)...)
	env, err := cel.NewEnv(cel.Declarations(opts...))
	if err != nil {
		return nil, nil, err
	}
	return env, []cel.ProgramOption{cel.Functions(fs...)}, nil
}
