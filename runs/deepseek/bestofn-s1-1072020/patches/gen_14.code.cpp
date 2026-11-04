Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    if (fields.empty())
        return FIT_NULL;

    Field* p = fields.data();
    Field* const end = p + fields.size();

    for (; p != end; ++p)
    {
        if (p->GetNum() == fieldNum)
            return p;
    }

    return FIT_NULL;
}
