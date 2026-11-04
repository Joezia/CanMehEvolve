    void SetAwakeningsCount(FIT_UINT8 awakeningsCount)
    {
        Field field;
        field.SetNum(11);
        field.SetSize(1);
        field.SetType(FIT_BASE_TYPE_UINT8);
        field.SetValue(&awakeningsCount, 1);
        SetField(field);
    }
