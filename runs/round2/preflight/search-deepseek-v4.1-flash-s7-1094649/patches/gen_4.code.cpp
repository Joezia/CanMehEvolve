    FIT_BOOL IsMinCoreTemperatureValid() const
    {
        const Field* field = GetField(159);
        return (FIT_NULL != field) ? field->IsValueValid() : FIT_FALSE;
    }
