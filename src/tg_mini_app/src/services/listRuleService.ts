import { client } from '@/api/client.gen';
import { apiData } from './apiRuntime';

export type ListTagRuleMode =
  | 'EXCLUDE'
  | 'INCLUDE_ONLY'
  | 'AUTO_ADD'
  | 'AUTO_REMOVE';

export interface ListTagRuleItem {
  tag_value: string;
  mode: ListTagRuleMode;
}

export interface ListTagRuleResponse extends ListTagRuleItem {
  id: string;
  list_id: string;
  created_at: string;
  updated_at: string | null;
  active: boolean;
}

export interface ListTagRulesResponse {
  items: ListTagRuleResponse[];
  count: number;
}

export interface KnownTagsResponse {
  tags: string[];
}

const base = (groupId: string, listId: string) =>
  `/api/v1/public/groups/${groupId}/lists/${listId}/rules`;

export const listRuleService = {
  getRules(groupId: string, listId: string): Promise<ListTagRulesResponse> {
    return apiData<ListTagRulesResponse>(
      client.get({ url: base(groupId, listId) } as any)
    );
  },

  putRules(
    groupId: string,
    listId: string,
    rules: ListTagRuleItem[]
  ): Promise<ListTagRulesResponse> {
    return apiData<ListTagRulesResponse>(
      client.put({
        url: base(groupId, listId),
        body: { rules },
      } as any)
    );
  },

  deleteRule(
    groupId: string,
    listId: string,
    ruleId: string
  ): Promise<string> {
    return apiData<string>(
      client.delete({
        url: `${base(groupId, listId)}/${ruleId}`,
      } as any)
    );
  },

  getKnownTags(groupId: string): Promise<KnownTagsResponse> {
    return apiData<KnownTagsResponse>(
      client.get({
        url: `/api/v1/public/groups/${groupId}/known-tags`,
      } as any)
    );
  },
};
