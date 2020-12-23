package manager

import (
	"context"
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	userstorage "github.com/HackerDom/ructfe2020/internal/storage/users"
	pb "github.com/HackerDom/ructfe2020/proto"
	"regexp"
)

type users struct {
	s userstorage.Users
}

func (m *users) GetUsers(ctx context.Context) ([]*pb.User, error) {
	users, err := m.s.List(ctx)
	if err != nil {
		return nil, err
	}
	return users, nil
}

func (m *users) GetNames(ctx context.Context) ([]string, error) {
	users, err := m.s.List(ctx)
	fmt.Println(users)
	if err != nil {
		return nil, err
	}
	names := make([]string, len(users))
	for i, user := range users {
		names[i] = user.Name
	}
	return names, nil
}

func (m *users) LoginUser(ctx context.Context, username, pass string) (*pb.LoginResponse, error) {
	if err := validateUsername(username); err != nil {
		return nil, err
	}
	panic("not implemented")
}

func (m *users) RegisterUser(ctx context.Context, username, pass, bio string) (*pb.User, error) {
	if err := validateUsername(username); err != nil {
		return nil, err
	}
	pass = hashutil.PersistDigest(pass)
	user := &pb.User{
		Name:     username,
		Password: pass,
		Bio:      bio,
	}
	err := m.s.Insert(ctx, user)
	if err != nil {
		return nil, err
	}
	return &pb.User{
		Name:     username,
		Password: pass,
		Bio:      bio,
	}, nil
}

const maxUsernameLen = 20
const minUsernameLen = 1
const usernameRegexp = "^[a-zA-Z0-9]*$"

func validateUsername(username string) error {
	if len(username) > maxUsernameLen {
		return fmt.Errorf("len(username) = %d; max = %d", len(username), maxUsernameLen)
	}
	if len(username) <= 0 {
		return fmt.Errorf("len(username) = %d; min = %d", len(username), minUsernameLen)
	}
	if ok, _ := regexp.MatchString(usernameRegexp, username); !ok {
		return fmt.Errorf("%s does not match '%s'", username, usernameRegexp)
	}
	return nil
}