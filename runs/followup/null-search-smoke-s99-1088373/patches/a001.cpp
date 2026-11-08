    FIT_BOOL IsStanceTimePercentValid() const
    {
        const Field* field = GetField(40);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-99-1
}
