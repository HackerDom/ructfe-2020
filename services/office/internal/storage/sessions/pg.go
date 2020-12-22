package sessions

import (
	"context"
	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"
)

var tokenToUserSchema = `CREATE TABLE IF NOT EXISTS tokens (
	token					TEXT PRIMARY KEY,
	name					TEXT
);`

type Sessions interface {
	Insert(ctx context.Context, name, session string) error
	Username(ctx context.Context, session string) error
}

func NewPg(db *sqlx.DB, l *zap.Logger) (Sessions, error) {
	_, erro := db.Exec(tokenToUserSchema)
	if erro != nil {
		return nil, erro
	}
	return &Pg{db: db, l: l}, nil
}

type Pg struct {
	db *sqlx.DB
	l  *zap.Logger
}

func (p *Pg) Insert(ctx context.Context, name, session string) error {
	panic("implement me")
}

func (p *Pg) Username(ctx context.Context, session string) error {
	panic("implement me")
}
