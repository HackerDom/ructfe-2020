package eval

import (
	"github.com/HackerDom/ructfe2020/pkg/eval/funcs"

	"github.com/google/cel-go/cel"

	"fmt"
)

func Eval(expr string, inerCtx map[string]string) (bool, error) {
	e, opts, err := createEnv(inerCtx)
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
	out, _, err := prg.Eval(getVarsIface(inerCtx))
	if err != nil {
		return false, err
	}
	res, ok := out.Value().(bool)
	if !ok {
		return false, fmt.Errorf("eval result should be <bool>, but was: '%v'", out.Value())
	}
	return res, nil
}

func createEnv(vars map[string]string) (*cel.Env, []cel.ProgramOption, error) {
	opts, fs := funcs.EnvOptions(vars)
	opts = append(opts, funcs.VarsDecls(getVarsIface(vars))...)
	env, err := cel.NewEnv(cel.Declarations(opts...))
	if err != nil {
		return nil, nil, err
	}
	return env, []cel.ProgramOption{cel.Functions(fs...)}, nil
}

func getVarsIface(vars map[string]string) map[string]interface{} {
	res := make(map[string]interface{}, len(vars))
	for k, v := range vars {
		res[k] = v
	}
	return res
}