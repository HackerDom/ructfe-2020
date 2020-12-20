package manager

import (
	"github.com/HackerDom/ructfe2020/internal/document"
	"github.com/HackerDom/ructfe2020/internal/storage/docs"
	userstorage "github.com/HackerDom/ructfe2020/internal/storage/users"
	pb "github.com/HackerDom/ructfe2020/proto"
)

type documents struct {
	s     docs.Documents
	users userstorage.Users
}

func (d *documents) Create(document *pb.Document) error {
	return d.s.Insert(document)
}

func (d *documents) Delete(docID string) error {
	return d.s.Delete(docID)
}

func (d *documents) ExecForUser(name, username string) (string, error) {
	docPB, err := d.s.Get(name)
	if err != nil {
		return "", err
	}
	doc := document.FromPB(docPB)
	users, err := d.users.List()
	if err != nil {
		return "", err
	}
	return doc.Execute(map[string]string{"username": username}, users)
}
