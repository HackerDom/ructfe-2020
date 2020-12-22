package users

import (
	"context"
	"fmt"
	pb "github.com/HackerDom/ructfe2020/proto"
	sq "github.com/Masterminds/squirrel"
	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"
	"strconv"
	"strings"
)

var usersSchema = `CREATE TABLE IF NOT EXISTS users (
    name					TEXT PRIMARY KEY,
	password                TEXT,
	bio                     TEXT
);`


type Users interface {
	List(ctx context.Context) ([]*pb.User, error)
	Insert(ctx context.Context, user *pb.User) error
}

func NewPg(db *sqlx.DB, l *zap.Logger) (Users, error) {
	_, err := db.Exec(usersSchema)
	if err != nil {
		return nil, err
	}
	return &Pg{db: db, l: l}, nil
}

type userModel struct {
	Name     string `db:"name"`
	Password string `db:"password"`
	Bio      string `db:"bio"`
}

type Pg struct {
	db *sqlx.DB
	l  *zap.Logger
}

func (u *Pg) Insert(ctx context.Context, user *pb.User) error {
	query, args, err := sq.Insert("users").Columns("name", "password", "bio").Values(user.Name, user.Password, user.Bio).ToSql()
	if err != nil {
		return err
	}
	u.l.Debug(fmt.Sprintf("Executing '%s': args: '%v'", query, args))
	_, err = u.db.ExecContext(ctx, ReplaceSQL(query, "?"), args...)
	if err != nil {
		return err
	}
	return err
}

func (u *Pg) List(ctx context.Context) ([]*pb.User, error) {
	var users []userModel
	err := u.db.SelectContext(ctx, &users, "SELECT name, password, bio FROM users;")
	if err != nil {
		return nil, err
	}
	usersProto := make([]*pb.User, len(users))
	for i, u := range users {
		usersProto[i] = &pb.User{
			Name:     u.Name,
			Password: u.Password,
			Bio:      u.Bio,
		}
	}
	return usersProto, nil
}

func ReplaceSQL(old, searchPattern string) string {
	tmpCount := strings.Count(old, searchPattern)
	for m := 1; m <= tmpCount; m++ {
		old = strings.Replace(old, searchPattern, "$"+strconv.Itoa(m), 1)
	}
	return old
}
