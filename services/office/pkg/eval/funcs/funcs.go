package funcs

import (
	"github.com/google/cel-go/checker/decls"
	"github.com/google/cel-go/common/types"
	"github.com/google/cel-go/common/types/ref"
	"github.com/google/cel-go/interpreter/functions"
	exprpb "google.golang.org/genproto/googleapis/api/expr/v1alpha1"
	"reflect"
)

func EnvOptions(inerCtx map[string]string) (decls []*exprpb.Decl, funcs []*functions.Overload) {
	funcs, funcsDecls := make([]*functions.Overload, 0), make([]*exprpb.Decl, 0)
	funcs, funcsDecls = UsefulFunc(inerCtx, funcs, funcsDecls)
	return funcsDecls, funcs
}

func VarsDecls(vars map[string]interface{}) []*exprpb.Decl {
	varsDecls := make([]*exprpb.Decl, 0)
	for name, val := range vars {
		switch reflect.TypeOf(val).Kind() {
		case reflect.String:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.String))
		case reflect.Slice:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.NewListType(decls.String)))
		case reflect.Int:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.Int))
		case reflect.Int32:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.Int))
		case reflect.Int64:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.Int))
		case reflect.Float64:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.Double))
		default:
			varsDecls = append(varsDecls, decls.NewVar(name, decls.Dyn))
		}
	}
	return varsDecls
}

func UsefulFunc(inerCtx map[string]string, funcs []*functions.Overload, declarations []*exprpb.Decl) ([]*functions.Overload, []*exprpb.Decl) {
	hasTag := func(tag string, inerCtx map[string]string) bool {
		return true
	}
	f, d := &functions.Overload{
		Operator: "has_tag_string",
		Unary: func(lhs ref.Val) ref.Val {
			val := lhs.Value().(string)
			return types.Bool(hasTag(val, inerCtx))
		},
	}, decls.NewFunction("has_tag",
		decls.NewOverload("has_tag_string",
			[]*exprpb.Type{decls.String},
			decls.Bool))
	return append(funcs, f), append(declarations, d)
}
