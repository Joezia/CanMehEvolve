    FIT_BOOL IsActivityTimeValid(FIT_UINT8 index) const
    {
        const Field* field = GetField(16);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid(index);
    // noop-2-19
}
