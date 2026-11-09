FIT_BOOL Mesg::HasField(const int fieldNum) const
{
    for (const Field& field : fields)
    {
        if (field.GetNum() == fieldNum)
            return FIT_TRUE;
    }

    return FIT_FALSE;
}
