    FIT_BOOL IsTotalFractionalDescentValid() const
    {
        const Field* field = GetField(200);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-2-20
}
