package users

import (
	"fmt"
	pb "github.com/HackerDom/ructfe2020/proto"
	sq "github.com/Masterminds/squirrel"
	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"
	"strconv"
	"strings"
	"time"
)

// TODO: [12/13/20] (vaspahomov):
var usersSchema = `CREATE TABLE IF NOT EXISTS users (
    name					TEXT PRIMARY KEY,
	password                   TEXT,
	bio                     TEXT
);`

var tokenToUserSchema = `CREATE TABLE IF NOT EXISTS tokens (
	token					TEXT PRIMARY KEY,
	name					TEXT
);`

const (
	maxOpenConn     = 20
	connMaxLifetime = time.Minute
)

type Users interface {
	List() ([]*pb.User, error)
	Insert(user *pb.User) error
}

func NewPg(db *sqlx.DB, l *zap.Logger) (Users, error) {
	_, err := db.Exec(usersSchema)
	if err != nil {
		return nil, err
	}
	_, erro := db.Exec(tokenToUserSchema)
	if erro != nil {
		return nil, erro
	}
	return &Pg{db: db, l: l}, nil
}

type userModel struct {
	Name  string `db:"name"`
	Token string `db:"token"`
	Bio   string `db:"bio"`
}

type Pg struct {
	db *sqlx.DB
	l  *zap.Logger
}

func (u *Pg) Insert(user *pb.User) error {
	query, args, err := sq.Insert("users").Columns("name", "token", "bio").Values(user.Name, user.Password, user.Bio).ToSql()
	if err != nil {
		return err
	}
	u.l.Debug(fmt.Sprintf("Executing '%s': args: '%v'", query, args))
	_, err = u.db.Exec(ReplaceSQL(query, "?"), args...)
	if err != nil {
		return err
	}
	return err
}

func (u *Pg) List() ([]*pb.User, error) {
	var users []userModel
	err := u.db.Select(&users, "SELECT name, token, bio FROM users;")
	if err != nil {
		return nil, err
	}
	usersProto := make([]*pb.User, len(users))
	for i, u := range users {
		usersProto[i] = &pb.User{
			Name:  u.Name,
			Password: u.Token,
			Bio:   u.Bio,
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
