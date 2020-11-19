package manager

type Manager struct {

}

func New() *Manager {
	return &Manager{}
}

func (m *Manager) GetUsers() []string {
	return []string{"biba", "boba"}
}
