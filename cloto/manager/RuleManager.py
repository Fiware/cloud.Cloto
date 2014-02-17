__author__ = 'gjp'
import datetime
import json
import uuid
from cloto.models import Rule, RuleModel, ListRuleModel, Entity, SpecificRule, Subscription, SubscriptionModel
from django.utils import timezone


class RuleManager():
    """This class provides methods to manage rules.
    """

    def get_rule_model(self):
        """Returns model of Rule."""
        return RuleModel

    def get_rule(self, ruleId):
        """Returns information about a general rule."""
        r_query = Rule.objects.get(ruleId__exact=ruleId)
        rule = RuleModel()
        rule.ruleId = r_query.__getattribute__("ruleId")
        rule.name = r_query.__getattribute__("name")
        rule.condition = r_query.__getattribute__("condition")
        rule.action = r_query.__getattribute__("action")
        return rule

    def delete_rule(self, ruleId):
        """Deletes a general rule."""
        r_query = Rule.objects.get(ruleId__exact=ruleId)
        r_query.delete()
        return True

    def get_all_rules(self, tenantId):
        """Returns all general rules of a tenant."""
        dict = list(Rule.objects.filter(tenantId=tenantId).values('ruleId', 'name', 'condition', 'action'))

        mylist = ListRuleModel()
        mylist.tenantId = tenantId
        mylist.rules = dict

        return mylist

    def create_general_rule(self, tenantId, rule):
        """Creates new general rule """
        condition = self.getContition(rule)
        action = self.getAction(rule)
        name = self.getName(rule)
        createdAt = datetime.datetime.now(tz=timezone.get_default_timezone())
        ruleId = uuid.uuid1()
        rule = Rule(ruleId=ruleId, tenantId=tenantId,
                    name=name, condition=condition, action=action, createdAt=createdAt)
        rule.save()
        ruleResult = RuleModel()
        ruleResult.ruleId = str(ruleId)
        return ruleResult

    def getContition(self, rule):
        """Splits contitions from a rule."""
        condition = json.loads(rule)['condition']
        return condition

    def getAction(self, rule):
        """Splits action from a rule."""
        action = json.loads(rule)['action']
        return action

    def getName(self, rule):
        """Splits the name from a rule."""
        name = json.loads(rule)['name']
        return name

    def create_specific_rule(self, tenantId, serverId, rule):
        """Creates new specific rule for a server."""
        try:
            entity = Entity.objects.get(entity_Id__exact=serverId)
        except Entity.DoesNotExist as err:
            entity = Entity(entity_Id=serverId, tenantId=tenantId)
            entity.save()

        condition = self.getContition(rule)
        action = self.getAction(rule)
        name = self.getName(rule)
        createdAt = datetime.datetime.now(tz=timezone.get_default_timezone())
        ruleId = uuid.uuid1()
        rule = SpecificRule(specificRule_Id=ruleId,
                            tenantId=tenantId, name=name, condition=condition, action=action, createdAt=createdAt)
        rule.save()
        entity.specificrules.add(rule)
        rule.save()
        ruleResult = RuleModel()
        ruleResult.ruleId = str(ruleId)
        return ruleResult

    def get_specific_rule(self, ruleId):
        """Returns information about a specific rule."""
        r_query = SpecificRule.objects.get(specificRule_Id__exact=ruleId)
        rule = RuleModel()
        rule.ruleId = r_query.__getattribute__("specificRule_Id")
        rule.name = r_query.__getattribute__("name")
        rule.condition = r_query.__getattribute__("condition")
        rule.action = r_query.__getattribute__("action")
        return rule

    def get_all_specific_rules(self, tenantId, serverId):
        """Returns all specific rules of a server."""
        entity = Entity.objects.get(entity_Id=serverId)

        mylist = entity.specificrules.values('specificRule_Id', 'name', 'condition', 'action').iterator()

        dictRules = list()
        for rule in mylist:
            dictRules.append(rule)
        subscr = entity.subscription.values('subscription_Id', 'ruleId').iterator()
        dictSubsc = list()
        for subs in subscr:
            dictSubsc.append(subs)

        mylist = ListRuleModel()
        mylist.tenantId = tenantId
        mylist.rules = dictRules
        mylist.serverId = serverId
        mylist.subscription = dictSubsc

        return mylist

    def delete_specific_rule(self, serverId, ruleId):
        """Deletes a specific rule."""
        r_query = SpecificRule.objects.get(specificRule_Id__exact=ruleId)
        r_query.delete()
        return True

    def create_specific_rule(self, tenantId, serverId, rule):
        """Creates new specific rule for a server."""
        try:
            entity = Entity.objects.get(entity_Id__exact=serverId)
        except Entity.DoesNotExist as err:
            entity = Entity(entity_Id=serverId, tenantId=tenantId)
            entity.save()

        condition = self.getContition(rule)
        action = self.getAction(rule)
        name = self.getName(rule)
        createdAt = datetime.datetime.now(tz=timezone.get_default_timezone())
        ruleId = uuid.uuid1()
        rule = SpecificRule(specificRule_Id=ruleId,
                            tenantId=tenantId, name=name, condition=condition, action=action, createdAt=createdAt)
        rule.save()
        entity.specificrules.add(rule)
        rule.save()
        ruleResult = RuleModel()
        ruleResult.ruleId = str(ruleId)
        return ruleResult

    def get_all_entities(self, tenantId):
        """Returns all servers with their information."""
        servers = Entity.objects.filter(tenantId__exact=tenantId)\
            .values('subscription', 'tenantId', 'entity_Id').iterator()

        dictEntities = list()
        for entity in servers:
            dictEntities.append(entity)

        mylist = ListRuleModel()
        mylist.servers = dictEntities

        return mylist

    def subscribe_to_rule(self, tenantId, serverId, subscription):
        """Creates a server subscription to a rule """
        try:
            entity = Entity.objects.get(entity_Id__exact=serverId)
        except Entity.DoesNotExist as err:
            entity = Entity(entity_Id=serverId, tenantId=tenantId)
            entity.save()

        ruleId = json.loads(subscription)['ruleId']
        url = json.loads(subscription)['url']
        subscription_Id = uuid.uuid1()
        subscr = Subscription(subscription_Id=subscription_Id, ruleId=ruleId, url=url, serverId=serverId)
        subscr.save()
        entity.subscription.add(subscr)
        entity.save()
        return subscription_Id

    def unsubscribe_to_rule(self, tenantId, serverId, subscriptionId):
        """Unsuscribe a server from a rule """
        r_query = Subscription.objects.get(subscription_Id__exact=subscriptionId)
        r_query.delete()
        return True

    def get_subscription(self, tenantId, serverId, subscriptionId):
        """Returns information about a subscription."""
        r_query = Subscription.objects.get(subscription_Id__exact=subscriptionId)
        subscription = SubscriptionModel()
        subscription.ruleId = r_query.__getattribute__("ruleId")
        subscription.serverId = r_query.__getattribute__("serverId")
        subscription.url = r_query.__getattribute__("url")
        subscription.subscriptionId = r_query.__getattribute__("subscription_Id")
        return subscription