    FIT_BOOL IsAutoActivityDetectStartTimestampValid() const
    {
        const Field* field = GetField(15);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        if( !CanSupportSubField( field, (FIT_UINT16) Profile::EVENT_MESG_START_TIMESTAMP_FIELD_AUTO_ACTIVITY_DETECT_START_TIMESTAMP ) )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid(0, (FIT_UINT16) Profile::EVENT_MESG_START_TIMESTAMP_FIELD_AUTO_ACTIVITY_DETECT_START_TIMESTAMP);
    // noop-2-10
}
