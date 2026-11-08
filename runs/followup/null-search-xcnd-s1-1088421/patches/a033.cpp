    FIT_BOOL IsEbikeTravelRangeValid() const
    {
        const Field* field = GetField(117);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-1-33
}
