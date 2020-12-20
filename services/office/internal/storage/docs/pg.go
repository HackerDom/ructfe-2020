package docs

import (
	"fmt"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"
	"google.golang.org/protobuf/proto"
)

type Documents interface {
	List() ([]*pb.Document, error)
	Insert(document *pb.Document) (int64, error)
	Delete(docID int64) error
	Get(name int64) (*pb.Document, error)
}

var docsSchema = `CREATE TABLE IF NOT EXISTS documents (
	id 						SERIAL PRIMARY KEY,
    content					BYTEA NOT NULL
);`

type doc struct {
	Id      string `db:"id"`
	Content []byte `db:"content"`
}

func (d *doc) Proto() (*pb.Document, error) {
	p := &pb.Document{}
	err := proto.Unmarshal(d.Content, p)
	if err != nil {
		return nil, err
	}
	return p, nil
}

func NewPg(db *sqlx.DB, l *zap.Logger) (Documents, error) {
	_, err := db.Exec(docsSchema)
	if err != nil {
		return nil, err
	}
	return &pg{db: db, l: l}, nil
}

type pg struct {
	db *sqlx.DB
	l  *zap.Logger
}

func (p *pg) List() ([]*pb.Document, error) {
	ds := make([]doc, 0)
	err := p.db.Select(&ds, "SELECT id, content FROM documents;")
	if err != nil {
		return nil, err
	}
	pdocs := make([]*pb.Document, len(ds))
	for i, d := range ds {
		pdocs[i], err = d.Proto()
		if err != nil {
			return nil, err
		}
	}
	return pdocs, nil
}

func (p *pg) Insert(document *pb.Document) (int64, error) {
	pr, err := proto.Marshal(document)
	if err != nil {
		return 0, err
	}
	row, err := p.db.Query("INSERT INTO documents (content) VALUES ($1) RETURNING id;", pr)
	if err != nil {
		return 0, err
	}
	id := int64(0)
	if !row.Next() {
		return 0, fmt.Errorf("not enougth returning rows")
	}
	err = row.Scan(&id)
	return id, err
}

func (p *pg) Delete(docID int64) error {
	_, err := p.db.Exec("DELETE (id, content) FROM documents WHERE id = $1;", docID)
	return err
}

func (p *pg) Get(id int64) (*pb.Document, error) {
	rows, err := p.db.Query("SELECT id, content FROM documents WHERE id = $1;", id)
	if err != nil {
		return nil, err
	}
	if !rows.Next() {
		return nil, fmt.Errorf("not enougth returning rows")
	}
	d := &doc{}
	fmt.Println()
	err = rows.Scan(&d.Id, &d.Content)
	if err != nil {
		return nil, err
	}
	return d.Proto()
}