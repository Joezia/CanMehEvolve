    FIT_BOOL IsMinHeartRateValid() const
    {
        const Field* field = GetField(64);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-2-18
}
