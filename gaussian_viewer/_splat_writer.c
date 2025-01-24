#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>

static PyObject* write_splat_data(PyObject* self, PyObject* args) {
    PyObject *buffer_obj, *indices_obj;
    PyArrayObject *xyz_arr, *scales_arr, *features_dc_arr, *opacities_arr, *rots_arr;
    
    if (!PyArg_ParseTuple(args, "OOOOOOO", &buffer_obj, &indices_obj, 
                         &xyz_arr, &scales_arr, &features_dc_arr, 
                         &opacities_arr, &rots_arr))
        return NULL;

    // Convert arrays to C-contiguous numpy arrays
    PyArrayObject *indices = (PyArrayObject*)PyArray_FROM_OTF(indices_obj, NPY_INT64, NPY_ARRAY_IN_ARRAY);
    xyz_arr = (PyArrayObject*)PyArray_FROM_OTF((PyObject*)xyz_arr, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);
    scales_arr = (PyArrayObject*)PyArray_FROM_OTF((PyObject*)scales_arr, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);
    features_dc_arr = (PyArrayObject*)PyArray_FROM_OTF((PyObject*)features_dc_arr, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);
    opacities_arr = (PyArrayObject*)PyArray_FROM_OTF((PyObject*)opacities_arr, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);
    rots_arr = (PyArrayObject*)PyArray_FROM_OTF((PyObject*)rots_arr, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);
    
    npy_intp n_vertices = PyArray_DIM(indices, 0);
    const int64_t *idx_ptr = (int64_t*)PyArray_DATA(indices);
    const float *xyz_ptr = (float*)PyArray_DATA(xyz_arr);
    const float *scales_ptr = (float*)PyArray_DATA(scales_arr);
    const float *features_ptr = (float*)PyArray_DATA(features_dc_arr);
    const float *opacities_ptr = (float*)PyArray_DATA(opacities_arr);
    const float *rots_ptr = (float*)PyArray_DATA(rots_arr);
    
    const double SH_C0 = 0.28209479177387814;
    
    for(npy_intp i = 0; i < n_vertices; i++) {
        int64_t idx = idx_ptr[i];
        float pos[3], scales[3];
        uint8_t color[4], rot[4];
        
        // Position
        for(int j = 0; j < 3; j++) {
            pos[j] = xyz_ptr[idx * 3 + j];
        }
        
        // Scales
        for(int j = 0; j < 3; j++) {
            scales[j] = expf(scales_ptr[idx * 3 + j]);
        }
        
        // Colors
        float opacity = 1.0f / (1.0f + expf(-opacities_ptr[idx]));
        for(int j = 0; j < 3; j++) {
            float c = 0.5f + SH_C0 * features_ptr[idx * 3 + j];
            color[j] = (uint8_t)(fmaxf(0.0f, fminf(255.0f, c * 255.0f)));
        }
        color[3] = (uint8_t)(opacity * 255.0f);
        
        // Rotation
        float rot_sum = 0.0f;
        float rot_raw[4];
        for(int j = 0; j < 4; j++) {
            rot_raw[j] = rots_ptr[idx * 4 + j];
            rot_sum += rot_raw[j] * rot_raw[j];
        }
        float rot_norm = sqrtf(rot_sum);
        for(int j = 0; j < 4; j++) {
            rot[j] = (uint8_t)(fmaxf(0.0f, fminf(255.0f, (rot_raw[j] / rot_norm) * 128.0f + 128.0f)));
        }
        
        // Write to buffer
        PyObject_CallMethod(buffer_obj, "write", "y#", pos, sizeof(pos));
        PyObject_CallMethod(buffer_obj, "write", "y#", scales, sizeof(scales));
        PyObject_CallMethod(buffer_obj, "write", "y#", color, sizeof(color));
        PyObject_CallMethod(buffer_obj, "write", "y#", rot, sizeof(rot));
    }
    
    Py_DECREF(indices);
    Py_DECREF(xyz_arr);
    Py_DECREF(scales_arr);
    Py_DECREF(features_dc_arr);
    Py_DECREF(opacities_arr);
    Py_DECREF(rots_arr);
    
    Py_RETURN_NONE;
}

static PyMethodDef SplatWriterMethods[] = {
    {"write_splat_data", write_splat_data, METH_VARARGS, "Write splat data to buffer"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef splat_writer_module = {
    PyModuleDef_HEAD_INIT,
    "_splat_writer",
    NULL,
    -1,
    SplatWriterMethods
};

PyMODINIT_FUNC PyInit__splat_writer(void) {
    import_array();
    return PyModule_Create(&splat_writer_module);
} 