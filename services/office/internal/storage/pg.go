package storage

import (
	pb "github.com/HackerDom/ructfe2020/proto"
	sq "github.com/Masterminds/squirrel"
	_ "github.com/jackc/pgx/v4"
	"github.com/jmoiron/sqlx"
	"net"
	"strconv"
	"strings"
	"time"
)

// TODO: [12/13/20] (vaspahomov):
var usersSchema = `CREATE TABLE users ....`

func NewPgUsers() (*UsersPg, error) {
	db, err := sqlx.Open("pgx", ConnString("", "", "", ""))
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(100)
	db.SetConnMaxLifetime(time.Minute)
	return &UsersPg{db: db}, nil
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

// ConnString constructs PostgreSQL connection string
func ConnString(addr, dbname, user, password string) string {
	var connParams []string

	host, port, err := net.SplitHostPort(addr)
	if err == nil {
		connParams = append(connParams, "host="+host)
		connParams = append(connParams, "port="+port)
	} else {
		connParams = append(connParams, "host="+addr)
	}

	if dbname != "" {
		connParams = append(connParams, "dbname="+dbname)
	}

	if user != "" {
		connParams = append(connParams, "user="+user)
	}

	if password != "" {
		connParams = append(connParams, "password="+password)
	}

	connParams = append(connParams, "sslmode="+"require")

	return strings.Join(connParams, " ")
}

func ReplaceSQL(old, searchPattern string) string {
	tmpCount := strings.Count(old, searchPattern)
	for m := 1; m <= tmpCount; m++ {
		old = strings.Replace(old, searchPattern, "$"+strconv.Itoa(m), 1)
	}
	return old
}

