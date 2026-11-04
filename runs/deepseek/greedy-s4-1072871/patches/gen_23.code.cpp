    FIT_BOOL IsIdValid() const
    {
        for (const Field& field : fields)
        {
            if (field.GetNum() == 14)
            {
                return field.IsValueValid();
            }
        }

        return FIT_FALSE;
    }
