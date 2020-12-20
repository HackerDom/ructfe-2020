package docs

import (
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/jmoiron/sqlx"
)

type Documents interface {
	List() ([]*pb.Document, error)
	Insert(document *pb.Document) error
	Delete(docID string) error
	Get(name string) (*pb.Document, error)
}

func NewPg(db *sqlx.DB) (Documents, error) {


	return &pg{db: db}, nil
}

type pg struct {
	db *sqlx.DB
}

func (p *pg) List() ([]*pb.Document, error) {

	panic("implement me")
}

func (p *pg) Insert(document *pb.Document) error {
	panic("implement me")
}

func (p *pg) Delete(docID string) error {
	panic("implement me")
}

func (p *pg) Get(name string) (*pb.Document, error) {
	panic("implement me")
}

