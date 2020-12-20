package storage

import (
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/storage/docs"
	"github.com/HackerDom/ructfe2020/internal/storage/users"
	_ "github.com/jackc/pgx/v4/stdlib"
	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"
	"net"
	"strings"
	"time"
)

const (
	Addr = "[::]"
	Port = "2379"
)

const (
	maxOpenConn     = 20
	connMaxLifetime = time.Minute
)

var (
	dialTimeout    = 2 * time.Second
	requestTimeout = 10 * time.Second
)

func Init(l *zap.Logger) (docs.Documents, users.Users, error) {
	conn, err := CreateConnection(l)
	if err != nil {
		return nil, nil, err
	}

	usersdb, err := users.NewPg(conn, l)
	if err != nil {
		return nil, nil, err
	}

	docksdb, err := docs.NewPg(conn)
	if err != nil {
		return nil, nil, err
	}

	return docksdb, usersdb, nil
}

func CreateConnection(l *zap.Logger) (*sqlx.DB, error) {
	connString := ConnString("postgres", "maindb", "test", "test")
	l.Info(fmt.Sprintf("Connecting to '%s'", connString))
	db, err := sqlx.Open("pgx", connString)
	if err != nil {
		return nil, err
	}
	l.Info(fmt.Sprintf("Setting MaxOpenConns to %d", maxOpenConn))
	l.Info(fmt.Sprintf("Setting ConnMaxLifetime to %s", connMaxLifetime))
	db.SetMaxOpenConns(maxOpenConn)
	db.SetConnMaxLifetime(connMaxLifetime)
	return db, nil
}

// ConnString constructs PostgreSQL connection string
func ConnString(addr, dbname, user, password string) string {
	var connParams []string

	host, port, err := net.SplitHostPort(addr)
	if err == nil {
		connParams = append(connParams, "host="+host)
		connParams = append(connParams, "port="+port)
	} else {
		connParams = append(connParams, "host="+addr)
	}

	if dbname != "" {
		connParams = append(connParams, "dbname="+dbname)
	}

	if user != "" {
		connParams = append(connParams, "user="+user)
	}

	if password != "" {
		connParams = append(connParams, "password="+password)
	}

	connParams = append(connParams, "sslmode="+"disable")

	return strings.Join(connParams, " ")
}
