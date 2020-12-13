package storage

import (
	pb "github.com/HackerDom/ructfe2020/proto"
	sq "github.com/Masterminds/squirrel"
	"github.com/jmoiron/sqlx"
	"strconv"
	"strings"
)

// TODO: [12/13/20] (vaspahomov):
var usersSchema = `CREATE TABLE users ....`

func NewPgUsers() *UsersPg {
	return &UsersPg{}
}

type userModel struct {
	name  string
	token string
}

type UsersPg struct {
	db *sqlx.DB
}

func (u *UsersPg) Insert(user *pb.User) error {
	query, args, err := sq.Insert("users").Columns("name", "token").Values(user.Name, user.Token).ToSql()
	if err != nil {
		return err
	}
	_, err = u.db.Exec(ReplaceSQL(query, "?"), args)
	if err != nil {
		return err
	}
	return err
}

func (u *UsersPg) List() ([]*pb.User, error) {
	query, args, err := sq.Select("*").From("users").ToSql()
	if err != nil {
		return nil, err
	}
	users := make([]*userModel, 0)
	err = u.db.Select(&users, ReplaceSQL(query, "?"), args)
	if err != nil {
		return nil, err
	}
	usersProto := make([]*pb.User, len(users))
	for i, u := range users {
		usersProto[i] = &pb.User{
			Name:  u.name,
			Token: u.token,
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

