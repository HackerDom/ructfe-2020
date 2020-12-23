package users

import (
	"context"
	"fmt"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"
)

var usersSchema = `CREATE TABLE IF NOT EXISTS users (
    name					TEXT PRIMARY KEY,
	password                TEXT,
	bio                     TEXT
);`


type Users interface {
	List(ctx context.Context) ([]*pb.User, error)
	Insert(ctx context.Context, user *pb.User) error
	User(ctx context.Context, name, pass string) (*pb.User, error)
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

func (s *Pg) Insert(ctx context.Context, user *pb.User) error {
	_, err := s.db.ExecContext(ctx, "INSERT INTO users (name, password, bio) VALUES ($1, $2, $3);", user.Name, user.Password, user.Bio)
	if err != nil {
		return err
	}
	return err
}

func (s *Pg) User(ctx context.Context, name string, pass string) (*pb.User, error) {
	var users []userModel
	err := s.db.SelectContext(ctx, &users, "SELECT name, password, bio FROM users WHERE name=$1 AND password=$2;", name, pass)
	if err != nil {
		return nil, err
	}
	if len(users) == 0 {
		return nil, fmt.Errorf("no such user exists")
	}
	userProto := &pb.User{
		Name: users[0].Name,
		Password: users[0].Password,
		Bio: users[0].Bio,
	}
	return userProto, err
}

func (s *Pg) List(ctx context.Context) ([]*pb.User, error) {
	var users []userModel
	err := s.db.SelectContext(ctx, &users, "SELECT name, password, bio FROM users;")
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
