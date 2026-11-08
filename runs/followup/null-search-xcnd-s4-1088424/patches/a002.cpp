    FIT_BOOL IsTotalWorkValid() const
    {
        const Field* field = GetField(41);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-4-2
}
