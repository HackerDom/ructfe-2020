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

func (d *documents) Create(document *pb.Document) (int64, error) {
	return d.s.Insert(document)
}

func (d *documents) Delete(docID int64) error {
	return d.s.Delete(docID)
}

func (d *documents) List() ([]*pb.ShortDocument, error) {
	ds, err := d.s.List()
	if err != nil {
		return nil, err
	}
	shorts := make([]*pb.ShortDocument, len(ds))
	for i, p := range ds {
		shorts[i] = document.FromPB(p).ShotProto()
	}
	return shorts, nil
}

func (d *documents) ExecForUser(id int64, username string) (string, error) {
	docPB, err := d.s.Get(id)
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
