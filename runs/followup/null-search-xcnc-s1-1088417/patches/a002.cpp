    FIT_BOOL IsStartPositionLongValid() const
    {
        const Field* field = GetField(22);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-1-2
}
