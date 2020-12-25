#include "sign.h"
#include "public.h"
#include "private.h"
#include "libnotary.h"


PyObject *libnotary_generate(PyObject *self, PyObject *args) {
    size_t private_size;
    uint8_t *private_data;
    private_t private;
    PyObject *private_bytes;

    private_init(private);

    do {
        if (!private_generate(private)) {
            private_clear(private);      
            Py_RETURN_NONE;
        }
    } while (!private_is_valid(private));

    private_serialize(&private_size, &private_data, private);

    private_bytes = PyBytes_FromStringAndSize((const char *)private_data, (ssize_t)private_size);
    free(private_data);

    private_clear(private);

    return private_bytes;
}


PyObject *libnotary_get_public(PyObject *self, PyObject *args) {
    public_t public;
    private_t private;
    size_t private_size, public_size;
    uint8_t *private_data, *public_data;
    PyObject *private_bytes, *public_bytes;

    if (!PyArg_ParseTuple(args, "S", &private_bytes)) {
        return NULL;
    }

    PyBytes_AsStringAndSize(private_bytes, (char **)(&private_data), (ssize_t *)(&private_size));

    private_init(private);
    
    if (!private_deserialize(private, private_size, private_data) || !private_is_valid(private)) {
        private_clear(private);
        Py_RETURN_NONE;
    }

    public_init(public);
    private_get_public(public, private);
    public_serialize(&public_size, &public_data, public);

    public_bytes = PyBytes_FromStringAndSize((const char *)public_data, (ssize_t)public_size);
    free(public_data);

    public_clear(public);
    private_clear(private);

    return public_bytes;
}


PyObject *libnotary_sign(PyObject *self, PyObject *args) {
    sign_t sign;
    private_t private;
    size_t private_size, content_size;
    uint8_t *private_data, *content_data;
    PyObject *sign_bytes, *private_bytes, *content_bytes;

    if (!PyArg_ParseTuple(args, "SS", &private_bytes, &content_bytes)) {
        return NULL;
    }

    PyBytes_AsStringAndSize(private_bytes, (char **)(&private_data), (ssize_t *)(&private_size));
    PyBytes_AsStringAndSize(content_bytes, (char **)(&content_data), (ssize_t *)(&content_size));

    private_init(private);

    if (!private_deserialize(private, private_size, private_data) || !private_is_valid(private)) {
        private_clear(private);
        Py_RETURN_NONE;
    }

    sign_init(sign);
    sign_create(sign, private, content_size, content_data);

    sign_bytes = PyBytes_FromStringAndSize((const char *)sign->data, (ssize_t)sign->length);
    sign_clear(sign);

    private_clear(private);

    return sign_bytes;
}


PyObject *libnotary_verify(PyObject *self, PyObject *args) {
    sign_t sign;
    public_t public;
    size_t public_size, content_size;
    uint8_t *public_data, *content_data;
    PyObject *sign_bytes, *public_bytes, *content_bytes;
    bool is_sign_correct;

    if (!PyArg_ParseTuple(args, "SSS", &public_bytes, &content_bytes, &sign_bytes)) {
        return NULL;
    }

    sign_init(sign);

    PyBytes_AsStringAndSize(public_bytes, (char **)(&public_data), (ssize_t *)(&public_size));
    PyBytes_AsStringAndSize(content_bytes, (char **)(&content_data), (ssize_t *)(&content_size));
    PyBytes_AsStringAndSize(sign_bytes, (char **)(&sign->data), (ssize_t *)(&sign->length));

    public_init(public);
    
    if (!public_deserialize(public, public_size, public_data)) {
        public_clear(public);
        Py_RETURN_NONE;
    }

    is_sign_correct = sign_verify(sign, public, content_size, content_data);

    public_clear(public);
    
    // do not clear sign because it was created from existing bytes
    // sign_clear(sign);

    if (is_sign_correct) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}


PyMethodDef libnotary_methods[] = {
    {"generate", libnotary_generate, METH_VARARGS, "Generate private key (for signing)"},
    {"get_public", libnotary_get_public, METH_VARARGS, "Get public key from private key (for verifying)"},
    {"sign", libnotary_sign, METH_VARARGS, "Sign data with private key"},
    {"verify", libnotary_verify, METH_VARARGS, "Verify signature of data with public key"},
    {NULL, NULL, 0, NULL}
};


struct PyModuleDef libnotary_module = {
    PyModuleDef_HEAD_INIT,
    "libnotary",
    "A tiny library for signing and verifying signatures",
    -1,
    libnotary_methods
};


PyObject *PyInit_libnotary(void) {
    return PyModule_Create(&libnotary_module);
}
