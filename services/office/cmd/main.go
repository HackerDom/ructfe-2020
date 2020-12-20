package main

import (
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/internal/server"
	"github.com/HackerDom/ructfe2020/internal/storage/docs"
	"github.com/HackerDom/ructfe2020/internal/storage/users"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"time"
)

func main() {
	l, _ := createLog().Build()
	usersStorage, _ := users.NewPg(l)
	docsStorage := docs.NewInMemory()
	err := server.RunServer(manager.New(usersStorage, docsStorage))
	if err != nil {
		panic(err)
	}
}

func createLog() *zap.Config {
	return &zap.Config{
		Level:       zap.NewAtomicLevelAt(zap.InfoLevel),
		Development: false,
		Sampling: &zap.SamplingConfig{
			Initial:    100,
			Thereafter: 100,
		},
		Encoding: "console",
		EncoderConfig: zapcore.EncoderConfig{
			TimeKey:       "ts",
			LevelKey:      "level",
			NameKey:       "logger",
			CallerKey:     "caller",
			MessageKey:    "msg",
			StacktraceKey: "stacktrace",
			LineEnding:    zapcore.DefaultLineEnding,
			EncodeLevel:   zapcore.LowercaseLevelEncoder,
			EncodeTime: func(t time.Time, enc zapcore.PrimitiveArrayEncoder) {
				enc.AppendString(t.Format("15:04:05.000"))
			},
			EncodeDuration: zapcore.SecondsDurationEncoder,
			EncodeCaller:   zapcore.ShortCallerEncoder,
		},
		OutputPaths:      []string{"stderr"},
		ErrorOutputPaths: []string{"stderr"},
	}
}