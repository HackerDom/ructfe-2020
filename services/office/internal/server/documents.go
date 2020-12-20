package server

import (
	"context"
	"github.com/HackerDom/ructfe2020/internal/document"
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/manager"
	httprpc "github.com/HackerDom/ructfe2020/pkg/httprtc"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/go-chi/chi"
	"github.com/golang/protobuf/proto"
)

func NewDocuments(m *manager.Manager) *documentsService {
	return &documentsService{m: m}
}

type documentsService struct {
	m *manager.Manager
}

func (s *documentsService) Mount(mux *chi.Mux) {
	httprpc.New("POST", "/docs/create").
		Mount(mux).
		WithJSONPbReader(&pb.CreateDocumentRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.Create(ctx, req.(*pb.CreateDocumentRequest))
		})
	httprpc.New("POST", "/docs/list").
		Mount(mux).
		WithJSONPbReader(&pb.ListDocumentsRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.List(ctx, req.(*pb.ListDocumentsRequest))
		})
	httprpc.New("POST", "/docs/execute").
		Mount(mux).
		WithJSONPbReader(&pb.ExecuteRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.Execute(ctx, req.(*pb.ExecuteRequest))
		})
}

func (s *documentsService) List(ctx context.Context, req *pb.ListDocumentsRequest) (*pb.ListDocumentsResponse, error) {
	// TODO: [12/20/20] (vaspahomov): pagination
	docs, err := s.m.List()
	if err != nil {
		return nil, err
	}
	return &pb.ListDocumentsResponse{Docs: docs}, nil
}

func (s *documentsService) Create(ctx context.Context, req *pb.CreateDocumentRequest) (*pb.CreateDocumentResponse, error) {
	d, err := document.Parse(req.Name, []byte(req.Doc))
	if err != nil {
		return nil, err
	}
	p := d.Proto()
	p.Token = hashutil.RandDigest(req.Name)
	id, err := s.m.Create(p)
	if err != nil {
		return nil, err
	}
	return &pb.CreateDocumentResponse{
		Id:    id,
		Token: p.Token,
	}, nil
}

func (s *documentsService) Execute(ctx context.Context, req *pb.ExecuteRequest) (*pb.ExecuteResponse, error) {
	executed, err := s.m.ExecForUser(req.DocId, req.Username)
	if err != nil {
		return nil, err
	}
	return &pb.ExecuteResponse{Executed: executed}, nil
}
