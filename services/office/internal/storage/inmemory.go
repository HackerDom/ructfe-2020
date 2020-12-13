package storage

func NewInMemoryUsers() *UsersInMemory {
	return &UsersInMemory{users: make([]string, 0)}
}

type UsersInMemory struct {
	users []string
}

func (u *UsersInMemory) Register(token string) error {
	u.users = append(u.users, token)
	return nil
}

func (u *UsersInMemory) List() ([]string, error) {
	return u.users, nil
}
