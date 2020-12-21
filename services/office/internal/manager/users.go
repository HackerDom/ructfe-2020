package manager

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	userstorage "github.com/HackerDom/ructfe2020/internal/storage/users"
	pb "github.com/HackerDom/ructfe2020/proto"
	"regexp"
)

type users struct {
	s userstorage.Users
}

func (m *users) GetUsers() ([]*pb.User, error) {
	users, err := m.s.List()
	if err != nil {
		return nil, err
	}
	return users, nil
}

func (m *users) GetNames() ([]string, error) {
	users, err := m.s.List()
	if err != nil {
		return nil, err
	}
	names := make([]string, len(users))
	for i, user := range users {
		names[i] = user.Name
	}
	return names, nil
}

func (m *users) LoginUser(username, pass string) (*pb.LoginResponse, error) {
	if ok, _ := regexp.MatchString("^[a-zA-Z0-9].$", username); !ok {
		return nil, errors.New("invalid login")
	}

	
}

func (m *users) RegisterUser(username, pass, bio string) (*pb.User, error) {
	if ok, _ := regexp.MatchString("^[a-zA-Z0-9].$", username); !ok {
		return nil, errors.New("invalid login")
	}

	pass = calcPassHash(pass)

	user := &pb.User{
		Name:  username,
		Password: pass,
		Bio: bio,
	}
	err := m.s.Insert(user)
	if err != nil {
		return nil, err
	}
	return &pb.User{
		Name:  username,
		Password: pass,
		Bio: bio,
	}, nil
}

func calcPassHash(pass string) string {
	hash := sha256.New()
	hash.Write([]byte(pass))
	digest := hash.Sum(make([]byte, 0))
	return hex.EncodeToString(digest)
}
