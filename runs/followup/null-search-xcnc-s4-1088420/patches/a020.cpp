    FIT_BOOL IsAutoPowerZeroValid() const
    {
        const Field* field = GetField(13);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-4-20
}
